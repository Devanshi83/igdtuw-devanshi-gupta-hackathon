# Historical Market Data Analysis

This document details an isolated historical analysis of real market responses to documented financial and geopolitical events. The goal is to calculate actual observed returns and provide context for market movements around stress events.

**Important Note**: These historical returns are calculated independently. They do not prove that a specific news article caused the entire price change, nor do they validate the synthetic shock percentages in our prototype's portfolio stress test.

## Methodology

- **Data Source**: Historical daily adjusted prices retrieved via the `yfinance` library.
- **Window Definition**: We calculate the window return from $T-1$ to $T+5$ (where $T=0$ is the event date). 
- **Return Formula**: `(Price_end - Price_start) / Price_start`
- **Missing Data Handling**: The implementation calculates windows using available trading days (ignoring weekends and holidays). Data is locally cached to `results/market_data/price_cache.csv` to ensure reproducibility without repeated network calls.
- **Benchmark**: The SPDR S&P 500 ETF Trust (`SPY`) is used as a baseline benchmark.

## Analyzed Events

We analyzed a small, defensible set of documented events:

1. **SVB Collapse (Bank Run Starts)**
   - **Date**: March 9, 2023
   - **Target Ticker**: `KRE` (SPDR S&P Regional Banking ETF)
   - **Source**: [Wikipedia - Collapse of SVB](https://en.wikipedia.org/wiki/Collapse_of_Silicon_Valley_Bank)
   
2. **Credit Suisse Liquidity Crisis**
   - **Date**: March 15, 2023
   - **Target Ticker**: `XLF` (Financial Select Sector SPDR Fund)
   - **Source**: [Wikipedia - Collapse of Credit Suisse](https://en.wikipedia.org/wiki/Collapse_of_Credit_Suisse)

3. **UK Mini-Budget Market Crash**
   - **Date**: September 23, 2022
   - **Target Ticker**: `EWU` (iShares MSCI United Kingdom ETF)
   - **Source**: [Wikipedia - Sept 2022 UK Mini-budget](https://en.wikipedia.org/wiki/September_2022_United_Kingdom_mini-budget)

## Actual Observations

| Event | Target Ticker | Target Return | Benchmark (SPY) Return | Excess Return |
|-------|---------------|---------------|------------------------|---------------|
| SVB Collapse (Bank Run Starts) | `KRE` | -19.91% | -0.70% | -19.21% |
| Credit Suisse Liquidity Crisis | `XLF` | -2.77% | +0.48% | -3.25% |
| UK Mini-Budget Market Crash | `EWU` | -5.52% | -4.55% | -0.96% |

*Data retrieved and processed dynamically. Observations and summary metrics are saved under `results/market_data/event_returns.csv` and `results/market_data/analysis_summary.json`.*

## Limitations

- The calculated window returns show correlation, not direct causation. Multiple confounding factors affect market prices on any given day.
- A 5-day post-event window is arbitrary and captures both under-reaction and over-reaction.
- The SVB event resulted in a massive draw-down in regional banking ETFs, reflecting systemic fears, whereas the Credit Suisse crisis effect on broad US Financials (`XLF`) was more muted.

## Reproducibility

To replicate this analysis offline (using the cached dataset) or online:

```sh
# Ensure dependencies are installed
python -m pip install -r requirements.txt

# Run the analysis script
python scripts/market_data/analyze_events.py
```

Automated tests for the return calculations can be run via:
```sh
pytest tests/test_market_analysis.py -q
```
