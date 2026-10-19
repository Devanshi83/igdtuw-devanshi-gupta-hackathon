"""Pure report construction shared by the UI, CLI and tests."""
import hashlib
import json
from datetime import datetime, timezone

import pandas as pd

from src.nlp.analyzer import analyze_text
from src.risk.stress import load_scenarios, stress_portfolio


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False,
                                    separators=(",", ":")).encode()).hexdigest()


def build_report(text, portfolio, scenario, intensity, issuer=None, *, analyst_reviewed=False):
    signal = analyze_text(text)
    if not text.strip():
        raise ValueError("Enter a headline before running a stress test")
    if signal["review_required"] and not analyst_reviewed:
        raise ValueError("Review the signal and explicitly confirm the scenario")
    definitions = load_scenarios()
    definition = definitions[scenario]
    issuer = issuer.strip() if issuer and definition["scope"] == "issuer" else None
    positions = stress_portfolio(portfolio, scenario, intensity, issuer)
    inputs = {
        "text": text, "portfolio": portfolio.to_dict(orient="records"),
        "scenario": scenario, "scenario_definition": definition,
        "intensity": intensity, "target_issuer": issuer,
        "model_version": signal["model_version"], "analyst_reviewed": analyst_reviewed,
    }
    before = float(positions.market_value.sum())
    pnl = float(positions.pnl.sum())
    eligible = positions.loc[positions.affected]
    # Explicit counterfactual: the SAME asset-type shocks applied to EVERY issuer.
    naive_pnl = float((positions.market_value * positions.base_shock_pct * intensity / 10).sum())
    warnings = list(signal["review_reasons"])
    if eligible.empty:
        warnings.append("No issuer match: zero P&L does not establish absence of risk")
    if not positions.shocked.any():
        warnings.append("No positions receive a non-zero shock")
    return {
        "schema_version": "1.0", "run_id": digest(inputs)[:16],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "inputs_sha256": digest(inputs), "inputs": inputs, "signal": signal,
        "summary": {
            "portfolio_before": before, "portfolio_after": before + pnl,
            "pnl": pnl, "pnl_pct": pnl / before * 100 if before else 0,
            "eligible_positions": int(positions.affected.sum()),
            "shocked_positions": int(positions.shocked.sum()),
            "eligible_exposure": float(eligible.market_value.sum()),
            "naive_all_issuer_pnl": naive_pnl,
            "scope_difference": pnl - naive_pnl,
        },
        "positions": positions.to_dict(orient="records"), "warnings": warnings,
        "limitations": [
            "Synthetic long-only portfolio; USD market values.",
            "Illustrative asset-type shocks, scaled linearly by intensity / 10.",
            "Intensity is a sensitivity setting, not a probability or confidence score.",
            "No causal loss prediction, calibrated VaR, contagion or derivative repricing.",
            "Issuer is selected by the analyst; it is not extracted from free text.",
        ],
    }


def scenario_comparison(portfolio, intensity, issuer):
    rows = []
    for name, definition in load_scenarios().items():
        values = stress_portfolio(portfolio, name, intensity,
                                  issuer if definition["scope"] == "issuer" else None)
        rows.append({"Scenario": name, "Scope": definition["scope"],
                     "P&L (USD)": float(values.pnl.sum()),
                     "Shocked positions": int(values.shocked.sum())})
    return pd.DataFrame(rows)


def sensitivity(portfolio, scenario, issuer):
    return pd.DataFrame([
        {"Intensity": level, "P&L (USD)": float(stress_portfolio(portfolio, scenario, level, issuer).pnl.sum())}
        for level in range(1, 11)
    ])
