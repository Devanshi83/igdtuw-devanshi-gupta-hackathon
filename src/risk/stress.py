SHOCKS = {
    "Geopolitical": {
        "Equity": -0.10, "Bond": -0.03,
        "Loan": -0.05, "Derivative": -0.04,
    },
    "Macroeconomic": {
        "Equity": -0.08, "Bond": -0.04,
        "Loan": -0.06, "Derivative": -0.05,
    },
    "Credit Event": {
        "Equity": -0.12, "Bond": -0.10,
        "Loan": -0.15, "Derivative": -0.08,
    },
    "Merger/Acquisition": {
        "Equity": 0.02, "Bond": 0.0,
        "Loan": 0.0, "Derivative": 0.0,
    },
    "Product/Cyber Event": {
        "Equity": -0.08, "Bond": -0.03,
        "Loan": -0.04, "Derivative": -0.02,
    },
    "Other": {
        "Equity": -0.02, "Bond": -0.01,
        "Loan": -0.01, "Derivative": -0.01,
    },
}


def stress_portfolio(portfolio, event, impact):
    """Apply an illustrative event shock; not a calibrated loss forecast."""
    if event not in SHOCKS:
        raise ValueError(f"Unsupported event category: {event}")
    if not isinstance(impact, (int, float)) or not 1 <= impact <= 10:
        raise ValueError("Impact must be between 1 and 10")

    required = {"asset_type", "market_value"}
    if not required.issubset(portfolio.columns):
        raise ValueError(f"Portfolio must contain columns: {sorted(required)}")
    if portfolio["market_value"].isna().any():
        raise ValueError("Market values cannot be missing")
    if (portfolio["market_value"] < 0).any():
        raise ValueError("Market values cannot be negative")

    result = portfolio.copy()
    result["shock_pct"] = (
        result["asset_type"].map(SHOCKS[event]).fillna(0.0) * impact / 10
    )
    result["value_after"] = (
        result["market_value"] * (1 + result["shock_pct"])
    )
    result["pnl"] = result["value_after"] - result["market_value"]
    return result
