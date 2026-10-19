import json
from numbers import Real
from pathlib import Path

import numpy as np
import pandas as pd

SCENARIO_PATH = (
    Path(__file__).resolve().parents[2] / "data" / "scenarios.json"
)


def load_scenarios():
    """Load scenario definitions and report configuration errors clearly."""
    try:
        with SCENARIO_PATH.open(encoding="utf-8") as file:
            scenarios = json.load(file)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"Could not load scenario configuration from {SCENARIO_PATH}: {exc}"
        ) from exc

    if not isinstance(scenarios, dict) or not scenarios:
        raise ValueError("Scenario configuration must be a non-empty object")

    return scenarios


def validate_scenario(scenario):
    """Validate a scenario before calculating portfolio risk."""
    if not isinstance(scenario, dict):
        raise ValueError("Scenario configuration must be an object")

    scope = scenario.get("scope")
    if not isinstance(scope, str) or scope not in {"issuer", "systemic"}:
        raise ValueError(
            f"Unsupported scenario scope: {scope!r}. "
            "Expected 'issuer' or 'systemic'."
        )

    shocks = scenario.get("shocks")
    if not isinstance(shocks, dict) or not shocks:
        raise ValueError("Scenario shocks must be a non-empty object")

    for asset_type, shock in shocks.items():
        if not isinstance(asset_type, str) or not asset_type.strip():
            raise ValueError("Shock asset types must be non-empty strings")

        if (
            not isinstance(shock, Real)
            or isinstance(shock, (bool, np.bool_))
        ):
            raise ValueError(f"Shock for {asset_type} must be a finite number")

        try:
            finite_shock = np.isfinite(shock)
        except (TypeError, ValueError, OverflowError):
            finite_shock = False

        if not finite_shock:
            raise ValueError(f"Shock for {asset_type} must be a finite number")

        if shock < -1:
            raise ValueError(
                f"Shock for {asset_type} cannot be less than -1 (-100%)"
            )

    return scenario


def stress_portfolio(portfolio, event, impact, target_company=None):
    """Apply documented illustrative shocks to eligible portfolio positions."""
    if (
        not isinstance(impact, Real)
        or isinstance(impact, (bool, np.bool_))
        or not np.isfinite(impact)
    ):
        raise ValueError("Impact must be a finite number between 1 and 10")

    if not 1 <= impact <= 10:
        raise ValueError("Impact must be between 1 and 10")

    if not isinstance(portfolio, pd.DataFrame) or portfolio.empty:
        raise ValueError("Portfolio must be a non-empty table")
    if not portfolio.columns.is_unique:
        raise ValueError("Portfolio columns must be unique")
    required = {"asset_type", "market_value"}
    if not required.issubset(portfolio.columns):
        raise ValueError(
            f"Portfolio must contain columns: {sorted(required)}"
        )

    if pd.api.types.is_bool_dtype(portfolio["market_value"]):
        raise ValueError("Market values must be numeric amounts, not booleans")
    if portfolio["asset_type"].isna().any():
        raise ValueError("Asset types cannot be missing")
    if portfolio["market_value"].isna().any():
        raise ValueError("Market values cannot be missing")

    if not pd.api.types.is_numeric_dtype(portfolio["market_value"]):
        raise ValueError("Market values must be numeric")

    try:
        market_values = portfolio["market_value"].to_numpy(dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Market values must be finite numeric values") from exc

    if not np.isfinite(market_values).all():
        raise ValueError("Market values must be finite")

    if (market_values < 0).any():
        raise ValueError("Market values cannot be negative")

    scenarios = load_scenarios()
    if event not in scenarios:
        raise ValueError(f"Unsupported event category: {event}")

    scenario = validate_scenario(scenarios[event])
    scope = scenario["scope"]
    shocks = scenario["shocks"]

    unknown_types = set(portfolio["asset_type"]) - set(shocks)
    if unknown_types:
        raise ValueError(f"No configured shock for asset types: {sorted(map(str, unknown_types))}")
    result = portfolio.copy()

    if scope == "issuer":
        if not isinstance(target_company, str) or not target_company.strip():
            raise ValueError(
                "Issuer-scoped scenarios require a target company"
            )

        if "issuer" not in result.columns:
            raise ValueError(
                "Issuer-scoped scenarios require an issuer column"
            )

        if result["issuer"].isna().any() or result["issuer"].astype(str).str.strip().eq("").any():
            raise ValueError("Issuer names cannot be missing for issuer scenarios")
        result["affected"] = (
            result["issuer"].astype(str).str.strip().str.casefold()
            == target_company.strip().casefold()
        )
    else:
        result["affected"] = True

    result["base_shock_pct"] = (
        result["asset_type"].map(shocks).fillna(0.0)
    )

    result["shock_pct"] = (
        result["base_shock_pct"]
        * (impact / 10.0)
        * result["affected"].astype(float)
    )

    result["shocked"] = result["affected"] & result["shock_pct"].ne(0)
    result["value_after"] = (
        result["market_value"] * (1 + result["shock_pct"])
    )
    result["pnl"] = result["value_after"] - result["market_value"]

    total_value = result["market_value"].sum()
    if total_value > 0:
        result["portfolio_weight_pct"] = (
            result["market_value"] / total_value * 100.0
        )
        result["pnl_pct_of_portfolio"] = (
            result["pnl"] / total_value * 100.0
        )
    else:
        result["portfolio_weight_pct"] = 0.0
        result["pnl_pct_of_portfolio"] = 0.0

    return result
