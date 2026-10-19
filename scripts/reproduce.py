"""Reproduce core demo and historical observations from committed data, offline."""
import json
import sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.reporting.report import build_report
from scripts.market_data.analyze_events import EVENTS, calculate_window_return


def reproduce():
    portfolio = pd.read_csv(ROOT / 'data/synthetic_portfolio.csv')
    report = build_report('Example Bank Ltd reported a major debt default and liquidity concerns.',
                          portfolio, 'Credit Event', 9, 'Example Bank Ltd')
    out = ROOT / 'results/demo'
    out.mkdir(parents=True, exist_ok=True)
    # Stable fixture: avoid a timestamp-only diff on every rerun.
    report.pop('generated_at_utc')
    (out / 'bank_credit_audit.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    cache = pd.read_csv(ROOT / 'data/market_data/price_cache.csv', parse_dates=['Date'])
    observations = []
    for event in EVENTS:
        target = calculate_window_return(cache.loc[cache.Ticker.eq(event['ticker'])], event['date'])
        benchmark = calculate_window_return(cache.loc[cache.Ticker.eq(event['benchmark'])], event['date'])
        if not target or not benchmark:
            raise ValueError(f"Incomplete cached window for {event['name']}")
        if (target['start_date'], target['end_date']) != (benchmark['start_date'], benchmark['end_date']):
            raise ValueError('Target and benchmark windows differ')
        observations.append({
            'event_name':event['name'], 'event_date':event['date'], 'ticker':event['ticker'],
            'benchmark':event['benchmark'], 'ticker_return_pct':target['return_pct'],
            'benchmark_return_pct':benchmark['return_pct'],
            'excess_return_pct':target['return_pct']-benchmark['return_pct'],
            'window_start':target['start_date'], 'window_end':target['end_date'],
            'source_url':event['source'],
        })
    pd.DataFrame(observations).to_csv(ROOT / 'results/market_data/event_returns.csv', index=False)
    print(f"Offline reproduction passed: bank credit P&L ${report['summary']['pnl']:,.0f}; {len(observations)} complete historical windows.")
    print(pd.DataFrame(observations)[['ticker','ticker_return_pct','benchmark_return_pct','excess_return_pct']].round(4).to_string(index=False))

if __name__ == '__main__':
    reproduce()
