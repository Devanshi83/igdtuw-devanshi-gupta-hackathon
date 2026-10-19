import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results" / "market_data"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = ROOT / "data" / "market_data" / "price_cache.csv"

EVENTS = [
    {
        "name": "SVB Collapse (Bank Run Starts)",
        "date": "2023-03-09",
        "ticker": "KRE",
        "benchmark": "SPY",
        "source": "https://en.wikipedia.org/wiki/Collapse_of_Silicon_Valley_Bank"
    },
    {
        "name": "Credit Suisse Liquidity Crisis",
        "date": "2023-03-15",
        "ticker": "XLF",
        "benchmark": "SPY",
        "source": "https://en.wikipedia.org/wiki/Collapse_of_Credit_Suisse"
    },
    {
        "name": "UK Mini-Budget Market Crash",
        "date": "2022-09-23",
        "ticker": "EWU",
        "benchmark": "SPY",
        "source": "https://en.wikipedia.org/wiki/September_2022_United_Kingdom_mini-budget"
    }
]

def load_cache():
    if CACHE_FILE.exists():
        try:
            df = pd.read_csv(CACHE_FILE, parse_dates=["Date"])
            # Ensure Date is timezone-naive
            if df["Date"].dt.tz is not None:
                df["Date"] = df["Date"].dt.tz_localize(None)
            return df
        except Exception as e:
            logger.warning(f"Could not load cache: {e}")
    return pd.DataFrame(columns=["Date", "Ticker", "Close"])

def save_cache(df):
    df.to_csv(CACHE_FILE, index=False)

def get_historical_data(ticker, start_date, end_date, cache_df):
    """
    Get historical data for a ticker. 
    Dates should be strings in YYYY-MM-DD format.
    """
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    
    # Filter cache
    cached_ticker = cache_df[cache_df["Ticker"] == ticker]
    if not cached_ticker.empty:
        # Check if we have the full range
        min_date = cached_ticker["Date"].min()
        max_date = cached_ticker["Date"].max()
        
        # Add a small buffer since non-trading days might make min/max look insufficient
        if min_date <= start_dt + timedelta(days=2) and max_date >= end_dt - timedelta(days=2):
            mask = (cached_ticker["Date"] >= start_dt) & (cached_ticker["Date"] <= end_dt)
            return cached_ticker[mask].copy()

    # Fetch from yfinance if not in cache or insufficient range
    logger.info(f"Fetching {ticker} from {start_date} to {end_date} via yfinance...")
    try:
        import yfinance as yf
        data = yf.download(ticker, start=start_date, end=end_date, progress=False, auto_adjust=True)
        if data.empty:
            logger.warning(f"No data found for {ticker}")
            return pd.DataFrame(columns=["Date", "Ticker", "Close"])
        
        # Flatten multi-index columns if present (yfinance sometimes does this)
        if isinstance(data.columns, pd.MultiIndex):
            # Just take the Close column for the specific ticker
            if "Close" in data.columns.levels[0]:
                closes = data["Close"]
            else:
                closes = data.iloc[:, 0] # fallback
        else:
            closes = data["Close"]
            
        # Reset index to get Date as a column
        df = closes.reset_index()
        # Rename columns in case of multi-index weirdness
        df.columns = ["Date", "Close"] 
        df["Ticker"] = ticker
        
        # Make Date timezone-naive
        if df["Date"].dt.tz is not None:
            df["Date"] = df["Date"].dt.tz_localize(None)
            
        return df
        
    except Exception as e:
        logger.error(f"Failed to fetch {ticker}: {e}")
        return pd.DataFrame(columns=["Date", "Ticker", "Close"])

def calculate_window_return(data_df, target_date_str, window_days=5):
    """
    Calculate return from (target_date - 1 trading day) to (target_date + window_days trading days).
    We use trading days instead of calendar days to avoid missing data.
    """
    if data_df.empty:
        return None
        
    if not isinstance(window_days, int) or isinstance(window_days, bool) or window_days < 0:
        raise ValueError("window_days must be a non-negative integer")
    if data_df["Date"].duplicated().any():
        raise ValueError("Duplicate trading dates")
    data_df = data_df.sort_values("Date").reset_index(drop=True)
    target_date = pd.to_datetime(target_date_str)
    
    # Find the index of the date closest to or equal to target_date
    # Target date is T=0
    future_dates = data_df[data_df["Date"] >= target_date]
    if future_dates.empty:
        return None
        
    t0_idx = future_dates.index[0]
    
    # T-1 is the trading day before T=0
    t_minus_1_idx = t0_idx - 1
    if t_minus_1_idx < 0:
        return None
        
    # T+window is window_days after T=0
    t_plus_window_idx = t0_idx + window_days
    if t_plus_window_idx >= len(data_df):
        return None  # Never label a partial window as T+5.
        
    price_start = float(data_df.iloc[t_minus_1_idx]["Close"])
    price_end = float(data_df.iloc[t_plus_window_idx]["Close"])
    
    if not all(pd.notna(v) and 0 < v < float("inf") for v in [price_start, price_end]):
        return None
        
    ret = (price_end - price_start) / price_start
    return {
        "start_date": data_df.iloc[t_minus_1_idx]["Date"].strftime("%Y-%m-%d"),
        "end_date": data_df.iloc[t_plus_window_idx]["Date"].strftime("%Y-%m-%d"),
        "start_price": price_start,
        "end_price": price_end,
        "return_pct": ret * 100
    }


def main():
    cache_df = load_cache()
    all_new_data = [cache_df]
    
    results = []
    
    for event in EVENTS:
        logger.info(f"Processing event: {event['name']} on {event['date']}")
        
        # We need roughly 10 calendar days before and 15 calendar days after to get 5 trading days
        start_date = (pd.to_datetime(event["date"]) - timedelta(days=20)).strftime("%Y-%m-%d")
        end_date = (pd.to_datetime(event["date"]) + timedelta(days=20)).strftime("%Y-%m-%d")
        
        # Get target ticker data
        ticker_df = get_historical_data(event["ticker"], start_date, end_date, cache_df)
        all_new_data.append(ticker_df)
        
        # Get benchmark data
        bench_df = get_historical_data(event["benchmark"], start_date, end_date, cache_df)
        all_new_data.append(bench_df)
        
        # Calculate returns
        ticker_ret = calculate_window_return(ticker_df, event["date"], window_days=5)
        bench_ret = calculate_window_return(bench_df, event["date"], window_days=5)
        
        if ticker_ret and bench_ret:
            results.append({
                "event_name": event["name"],
                "event_date": event["date"],
                "ticker": event["ticker"],
                "benchmark": event["benchmark"],
                "ticker_return_pct": ticker_ret["return_pct"],
                "benchmark_return_pct": bench_ret["return_pct"],
                "excess_return_pct": ticker_ret["return_pct"] - bench_ret["return_pct"],
                "window_start": ticker_ret["start_date"],
                "window_end": ticker_ret["end_date"],
                "source_url": event.get("source", "")
            })
        else:
            logger.warning(f"Could not calculate returns for {event['name']}")
            
    # Update cache
    if all_new_data:
        updated_cache = pd.concat(all_new_data, ignore_index=True).drop_duplicates(subset=["Date", "Ticker"])
        save_cache(updated_cache)
        
    # Save results
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_DIR / "event_returns.csv", index=False)
    
    with open(RESULTS_DIR / "analysis_summary.json", "w") as f:
        json.dump({
            "retrieval_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "yfinance",
            "events_analyzed": len(results),
            "observations": results
        }, f, indent=2)
        
    logger.info("Market data analysis complete.")
    for r in results:
        logger.info(f"{r['event_name']} ({r['ticker']}): {r['ticker_return_pct']:.2f}% (Bench: {r['benchmark_return_pct']:.2f}%)")

if __name__ == "__main__":
    main()
