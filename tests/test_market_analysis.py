import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

import pandas as pd
import pytest

from scripts.market_data.analyze_events import calculate_window_return

def test_calculate_window_return_normal():
    # Setup offline fixture
    dates = pd.date_range("2023-03-01", periods=10, freq="B") # business days
    prices = [100.0, 105.0, 110.0, 100.0, 90.0, 80.0, 85.0, 90.0, 95.0, 100.0]
    df = pd.DataFrame({"Date": dates, "Close": prices})
    
    # Event date: 2023-03-07 (T=0, which is index 4, price 90)
    # T-1 is index 3, price 100.0
    # Window = 5 trading days after T=0. T+1, T+2, T+3, T+4, T+5. 
    # Index 4 + 5 = 9. Index 9 price is 100.0.
    
    ret = calculate_window_return(df, "2023-03-07", window_days=5)
    
    assert ret is not None
    assert ret["start_price"] == 100.0
    assert ret["end_price"] == 100.0
    assert ret["return_pct"] == pytest.approx(0.0)
    
def test_calculate_window_return_empty_df():
    df = pd.DataFrame(columns=["Date", "Close"])
    ret = calculate_window_return(df, "2023-03-07")
    assert ret is None

def test_calculate_window_return_no_future_data():
    dates = pd.date_range("2023-03-01", periods=3, freq="B")
    prices = [100.0, 105.0, 110.0]
    df = pd.DataFrame({"Date": dates, "Close": prices})
    
    ret = calculate_window_return(df, "2023-03-10")
    assert ret is None
