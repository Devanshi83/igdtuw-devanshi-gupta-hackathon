"""Integration and regression checks against independently calculated examples."""
import json
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

from src.nlp.analyzer import analyze_text
from src.reporting.report import build_report, digest, scenario_comparison, sensitivity
from src.risk.stress import stress_portfolio
from scripts.market_data.analyze_events import calculate_window_return

ROOT = Path(__file__).resolve().parents[1]

@pytest.fixture
def portfolio():
    return pd.read_csv(ROOT / 'data/synthetic_portfolio.csv')


def test_bank_loss_reconciles_to_manual_positions(portfolio):
    r = build_report('Bank default and liquidity concerns', portfolio, 'Credit Event', 9, 'Example Bank Ltd')
    # 200k equity * -10.8%, 250k loan * -13.5%, 100k swap * -7.2%.
    assert r['summary']['pnl'] == pytest.approx(-62550)
    assert r['summary']['portfolio_after'] == pytest.approx(1087450)
    assert r['summary']['naive_all_issuer_pnl'] == pytest.approx(-121050)
    assert r['summary']['scope_difference'] == pytest.approx(58500)
    assert r['summary']['eligible_exposure'] == 550000
    assert sum(p['pnl'] for p in r['positions']) == pytest.approx(r['summary']['pnl'])
    assert r['inputs_sha256'] == digest(r['inputs'])
    json.dumps(r, allow_nan=False)


def test_report_contains_replayable_inputs(portfolio):
    r = build_report('A cybersecurity breach', portfolio, 'Product/Cyber Event', 6, 'Example Technology Ltd')
    replay = stress_portfolio(pd.DataFrame(r['inputs']['portfolio']), r['inputs']['scenario'],
                              r['inputs']['intensity'], r['inputs']['target_issuer'])
    assert replay.pnl.sum() == pytest.approx(-14700)
    assert r['summary']['pnl'] == pytest.approx(-14700)
    changed = build_report('A cybersecurity breach', portfolio, 'Product/Cyber Event', 7, 'Example Technology Ltd')
    assert changed['run_id'] != r['run_id']


@pytest.mark.parametrize('text', ['The bank denies default', 'War and default', 'Annual meeting today'])
def test_uncertain_signals_require_explicit_review(portfolio, text):
    assert analyze_text(text)['review_required']
    with pytest.raises(ValueError, match='Review'):
        build_report(text, portfolio, 'Credit Event', 9, 'Example Bank Ltd')
    assert build_report(text, portfolio, 'Credit Event', 9, 'Example Bank Ltd', analyst_reviewed=True)['warnings']


def test_known_keyword_evidence_and_unchanged_sentiment():
    signal = analyze_text('The bank reported a debt default and liquidity concerns.')
    assert signal['evidence']['category_matches'] == {'Credit Event': ['default', 'liquidity']}
    assert signal['sentiment_score'] == -1
    assert not signal['review_required']


def test_zero_shock_is_distinct_from_eligible(portfolio):
    r = stress_portfolio(portfolio, 'Merger/Acquisition', 5, 'Example Technology Ltd')
    assert r.affected.sum() == 2
    assert r.shocked.sum() == 1
    assert r.pnl.sum() == pytest.approx(2500)


@pytest.mark.parametrize('market_value', [True, float('nan'), float('inf'), -1, '100'])
def test_bad_uploaded_market_values_rejected(market_value):
    with pytest.raises(ValueError):
        stress_portfolio(pd.DataFrame({'asset_type':['Equity'], 'market_value':[market_value]}), 'Geopolitical', 9)


def test_unsupported_asset_is_not_silently_zero():
    with pytest.raises(ValueError, match='No configured shock'):
        stress_portfolio(pd.DataFrame({'asset_type':['Option'], 'market_value':[100]}), 'Geopolitical', 9)


def test_partial_historical_window_rejected():
    df = pd.DataFrame({'Date':pd.date_range('2023-03-01', periods=4, freq='B'), 'Close':[100, 101, 98, 97]})
    assert calculate_window_return(df, '2023-03-02', 5) is None


def test_sensitivity_and_scenarios_reconcile(portfolio):
    curve = sensitivity(portfolio, 'Credit Event', 'Example Bank Ltd')
    assert curve['P&L (USD)'].iloc[0] == pytest.approx(-6950)
    assert curve['P&L (USD)'].iloc[-1] == pytest.approx(-69500)
    assert curve['P&L (USD)'].is_monotonic_decreasing
    rows = scenario_comparison(portfolio, 9, 'Example Bank Ltd')
    assert rows.loc[rows.Scenario.eq('Credit Event'), 'P&L (USD)'].iloc[0] == pytest.approx(-62550)


def test_app_run_download_rerun_and_stale_state():
    at = AppTest.from_file(str(ROOT / 'app.py'), default_timeout=20).run()
    assert not at.exception
    at.button[0].click().run()
    assert not at.exception
    assert any('$-14,700' == m.value for m in at.metric)
    at.run()  # A download/rerun must not discard a completed analysis.
    assert any('$-14,700' == m.value for m in at.metric)
    at.slider[0].set_value(7).run()
    assert any('Inputs changed' in info.value for info in at.info)
    assert not any('$-14,700' == m.value for m in at.metric)
