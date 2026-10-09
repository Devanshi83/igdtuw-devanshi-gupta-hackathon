import pandas as pd
import pytest

from src.nlp.analyzer import analyze_text
from src.risk.stress import stress_portfolio


def test_negative_credit_event_is_classified():
    result = analyze_text(
        "The bank reported a major debt default and liquidity concerns."
    )
    assert result["event_classification"] == "Credit Event"
    assert result["sentiment_score"] < 0
    assert result["impact_score"] == 9


def test_positive_text_has_positive_sentiment():
    result = analyze_text(
        "The company reported strong profit growth and record revenue."
    )
    assert result["sentiment_score"] == 1.0


def test_neutral_text_has_zero_sentiment():
    result = analyze_text("The company held its annual meeting.")
    assert result["sentiment_score"] == 0.0
    assert result["event_classification"] == "Other"


def test_empty_text_is_handled():
    result = analyze_text("")
    assert result["sentiment_score"] == 0.0
    assert result["event_classification"] == "Other"


def test_non_string_text_is_rejected():
    with pytest.raises(TypeError):
        analyze_text(None)


def test_impact_must_be_between_one_and_ten():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "market_value": [1000.0],
    })
    with pytest.raises(ValueError):
        stress_portfolio(portfolio, "Credit Event", 11)


def test_credit_stress_calculates_expected_values():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity", "Bond", "Loan", "Derivative"],
        "market_value": [1000.0, 1000.0, 1000.0, 1000.0],
    })

    result = stress_portfolio(portfolio, "Credit Event", 10)

    assert result["value_after"].tolist() == [
        880.0, 900.0, 850.0, 920.0
    ]
    assert result["pnl"].sum() == pytest.approx(-450.0)


def test_original_portfolio_is_not_mutated():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "market_value": [1000.0],
    })
    original = portfolio.copy(deep=True)

    stress_portfolio(portfolio, "Credit Event", 10)

    pd.testing.assert_frame_equal(portfolio, original)


def test_unknown_event_is_rejected():
    portfolio = pd.DataFrame({
        "asset_type": ["Equity"],
        "market_value": [1000.0],
    })
    with pytest.raises(ValueError):
        stress_portfolio(portfolio, "Unknown Event", 5)
