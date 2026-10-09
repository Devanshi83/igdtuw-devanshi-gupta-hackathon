import json
from pathlib import Path

import pandas as pd

SCENARIO_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "scenarios.json"
)


def load_scenarios():
    with SCENARIO_PATH.open(encoding="utf-8") as file:
        scenarios = json.load(file)

    if not isinstance(scenarios, dict) or not scenarios:
        raise ValueError("Scenario configuration must be a non-empty object")

    return scenarios


def stress_portfolio(portfolio, event, impact, target_company=None):
    """Apply documented illustrative shocks to eligible portfolio positions."""
    if not isinstance(impact, (int, float)) or isinstance(impact, bool):
        raise ValueError("Impact must be a number between 1 and 10")
    if not 1 <= impact <= 10:
        raise ValueError("Impact must be between 1 and 10")

    required = {"asset_type", "market_value"}
    if not required.issubset(portfolio.columns):
        raise ValueError(
            f"Portfolio must contain columns: {sorted(required)}"
        )

    if portfolio["market_value"].isna().any():
        raise ValueError("Market values cannot be missing")

    if not pd.api.types.is_numeric_dtype(portfolio["market_value"]):
        raise ValueError("Market values must be numeric")

    if (portfolio["market_value"] < 0).any():
        raise ValueError("Market values cannot be negative")

    scenarios = load_scenarios()
    if event not in scenarios:
        raise ValueError(f"Unsupported event category: {event}")

    scenario = scenarios[event]
    scope = scenario["scope"]
    shocks = scenario["shocks"]

    result = portfolio.copy()

    if scope == "issuer" and target_company:
        if "issuer" not in result.columns:
            raise ValueError(
                "Issuer-scoped scenarios require an issuer column"
            )
        result["affected"] = (
            result["issuer"].astype(str).str.casefold()
            == target_company.strip().casefold()
        )
    elif scope == "issuer":
        # Without a target, retain portfolio-wide behavior for generic
        # calculations and backward-compatible unit tests.
        result["affected"] = True
    elif scope == "systemic":
        result["affected"] = True
    else:
        raise ValueError(f"Unsupported scenario scope: {scope}")

    result["base_shock_pct"] = (
        result["asset_type"].map(shocks).fillna(0.0)
    )

    result["shock_pct"] = (
        result["base_shock_pct"]
        * (impact / 10.0)
        * result["affected"].astype(float)
    )

    result["value_after"] = (
        result["market_value"] * (1 + result["shock_pct"])
    )
    result["pnl"] = result["value_after"] - result["market_value"]

    return result
