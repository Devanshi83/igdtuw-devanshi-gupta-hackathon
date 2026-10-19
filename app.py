import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.nlp.analyzer import analyze_text
from src.risk.stress import load_scenarios, stress_portfolio

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

SOURCE_FILES = {
    "Financial news": "sample_news.json",
    "Social-media posts": "sample_social_posts.json",
}


@st.cache_data
def load_records(filename):
    with (DATA / filename).open(encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(f"{filename} must contain a JSON list")
    if not all(isinstance(record, dict) for record in records):
        raise ValueError(f"{filename} must contain JSON objects")

    return records


@st.cache_data
def load_portfolio():
    portfolio = pd.read_csv(DATA / "synthetic_portfolio.csv")
    required = {"asset_id", "asset_name", "asset_type", "market_value"}
    missing = required - set(portfolio.columns)

    if missing:
        raise ValueError(f"Portfolio is missing columns: {sorted(missing)}")

    return portfolio


st.set_page_config(
    page_title="Signal-to-Shock",
    page_icon="📊",
    layout="wide",
)

st.title("Signal-to-Shock")
st.caption(
    "Financial event intelligence and portfolio stress testing | "
    "Synthetic-data prototype"
)

st.info(
    "This prototype uses a transparent keyword baseline and illustrative "
    "scenario shocks. Results are sensitivity estimates, not market forecasts."
)

try:
    source = st.selectbox("Input source", list(SOURCE_FILES))
    records = load_records(SOURCE_FILES[source])

    if not records:
        st.error("No sample records are available for this source.")
        st.stop()

    record = st.selectbox(
        "Select a sample record",
        records,
        format_func=lambda item: (
            f"{item.get('id', 'Unknown ID')} — "
            f"{item.get('company', 'Unknown company')}"
        ),
    )

    text = st.text_area(
        "Text to analyze",
        value=record.get("text", ""),
        height=140,
        help="Edit the sample text to explore how the keyword baseline responds.",
    )

    portfolio = load_portfolio()
    scenarios = load_scenarios()

except (OSError, ValueError, json.JSONDecodeError) as exc:
    st.error(f"Unable to load the prototype's input data: {exc}")
    st.stop()

starting_value = float(portfolio["market_value"].sum())

st.subheader("Portfolio overview")
overview_left, overview_right, overview_third = st.columns(3)
overview_left.metric("Starting portfolio value", f"${starting_value:,.2f}")
overview_right.metric("Portfolio positions", f"{len(portfolio)}")
overview_third.metric("Available scenarios", f"{len(scenarios)}")

st.divider()
st.subheader("1. Event analysis")

try:
    signal = analyze_text(text)
except (TypeError, ValueError) as exc:
    st.error(f"Unable to analyze this text: {exc}")
    st.stop()

event_col, sentiment_col, impact_col = st.columns(3)
event_col.metric("Detected event", signal["event_classification"])
sentiment_col.metric("Keyword sentiment", f"{signal['sentiment_score']:+.3f}")
impact_col.metric("Baseline impact score", f"{signal['impact_score']}/10")

with st.expander("How was this signal produced?"):
    st.write(
        "The current analyzer matches configured event keywords and counts "
        "predefined positive and negative words. It is a rule-based baseline, "
        "not a trained NLP model."
    )
    st.json(signal["evidence"])

st.divider()
st.subheader("2. Configure a stress test")
st.write(
    "Choose a scenario independently of the detected impact score. "
    "This lets you explore lower-impact events and hypothetical situations."
)

scenario_names = list(scenarios)
detected_event = signal["event_classification"]
default_scenario_index = (
    scenario_names.index(detected_event)
    if detected_event in scenario_names
    else 0
)

scenario_name = st.selectbox(
    "Stress scenario",
    scenario_names,
    index=default_scenario_index,
)
scenario = scenarios[scenario_name]

st.caption(
    "Scope: "
    + (
        "Issuer-specific — only positions matching the selected issuer are shocked."
        if scenario.get("scope") == "issuer"
        else "Systemic — all portfolio positions are eligible for the configured shocks."
    )
)

stress_intensity = st.slider(
    "Stress intensity",
    min_value=1,
    max_value=10,
    value=int(signal["impact_score"]),
    help=(
        "Scales the configured scenario shocks linearly. "
        "This is a user-selected sensitivity parameter, not a probability."
    ),
)

target_company = record.get("company", "")
if scenario.get("scope") == "issuer":
    target_company = st.text_input(
        "Target issuer",
        value=str(target_company),
        help="Must match an issuer in the synthetic portfolio for positions to be affected.",
    )
else:
    st.caption("The target issuer is not used for systemic scenarios.")

with st.expander("Configured scenario shocks"):
    st.write(
        "The following base shocks are scaled by stress intensity / 10. "
        "Positions whose asset types are not listed receive no configured shock."
    )
    shock_table = pd.DataFrame(
        [
            {
                "Asset type": asset_type,
                "Base shock (%)": round(float(shock) * 100, 2),
            }
            for asset_type, shock in scenario["shocks"].items()
        ]
    )
    st.dataframe(shock_table, width="stretch", hide_index=True)

if st.button("Run portfolio stress test", type="primary"):
    try:
        stressed = stress_portfolio(
            portfolio=portfolio,
            event=scenario_name,
            impact=stress_intensity,
            target_company=target_company if scenario.get("scope") == "issuer" else None,
        )
    except (ValueError, TypeError, KeyError) as exc:
        st.error(f"Stress test could not be completed: {exc}")
        st.stop()

    before = float(stressed["market_value"].sum())
    after = float(stressed["value_after"].sum())
    pnl = float(stressed["pnl"].sum())
    affected_count = int(stressed["affected"].sum())
    pnl_pct = (pnl / before * 100) if before > 0 else 0.0

    st.divider()
    st.subheader("3. Stress test results")

    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    metric_a.metric("Before stress", f"${before:,.2f}")
    metric_b.metric("After stress", f"${after:,.2f}")
    metric_c.metric(
        "Simulated P&L",
        f"${pnl:,.2f}",
        delta=f"{pnl_pct:+.2f}% of portfolio",
        delta_color="normal",
    )
    metric_d.metric("Affected positions", f"{affected_count} / {len(stressed)}")

    if affected_count == 0:
        st.warning(
            "No positions matched this scenario. Check the target issuer "
            "and the issuer names in the portfolio."
        )

    st.caption(
        f"Scenario: {scenario_name} | Intensity: {stress_intensity}/10 | "
        f"Scope: {scenario['scope']}"
    )

    display_columns = [
        column
        for column in [
            "asset_name",
            "asset_type",
            "issuer",
            "market_value",
            "portfolio_weight_pct",
            "affected",
            "shock_pct",
            "value_after",
            "pnl",
            "pnl_pct_of_portfolio",
        ]
        if column in stressed.columns
    ]

    display_data = stressed[display_columns].copy()
    percent_columns = [
        column
        for column in ["portfolio_weight_pct", "shock_pct", "pnl_pct_of_portfolio"]
        if column in display_data.columns
    ]
    for column in percent_columns:
        if column == "shock_pct":
            display_data[column] = display_data[column] * 100

    st.write("Position-level results")
    st.dataframe(display_data, width="stretch", hide_index=True)

    st.write("Simulated P&L by position")
    chart_data = stressed.set_index("asset_name")[["pnl"]]
    st.bar_chart(chart_data)

    st.download_button(
        "Download stress results (CSV)",
        data=stressed.to_csv(index=False).encode("utf-8"),
        file_name="signal_to_shock_stress_results.csv",
        mime="text/csv",
    )

    output_dir = DATA / "outputs"
    output_dir.mkdir(exist_ok=True)
    report = {
        "record_id": record.get("id"),
        "company": record.get("company"),
        "source": record.get("source", source),
        "signal": signal,
        "stress_test": {
            "scenario": scenario_name,
            "scope": scenario["scope"],
            "intensity": stress_intensity,
            "target_company": (
                target_company if scenario.get("scope") == "issuer" else None
            ),
            "portfolio_before": before,
            "portfolio_after": after,
            "pnl": pnl,
            "pnl_pct_of_portfolio": pnl_pct,
            "affected_positions": affected_count,
            "total_positions": len(stressed),
        },
        "assumptions": (
            "Synthetic portfolio and illustrative shocks; not calibrated "
            "forecasts or investment advice."
        ),
    }
    (output_dir / "latest_signal.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

st.divider()
st.caption(
    "All portfolio data and sample records are synthetic. The keyword "
    "baseline and configured shocks are illustrative and are not calibrated "
    "market forecasts or investment advice."
)
