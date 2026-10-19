"""Offline analyst workbench. Run: python -m streamlit run app.py."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.nlp.analyzer import analyze_text
from src.reporting.report import build_report, scenario_comparison, sensitivity
from src.risk.stress import load_scenarios, stress_portfolio

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
st.set_page_config(page_title="Signal-to-Shock | Risk workbench", page_icon="◈", layout="wide")
st.markdown("""<style>
.block-container {max-width:1400px;padding-top:2rem;}
h1 {font-family:Georgia,serif;font-weight:500!important;font-size:3.4rem!important;letter-spacing:-1.5px;}
h2,h3 {letter-spacing:-.5px;}
[data-testid="stMetricValue"] {font-variant-numeric:tabular-nums;}
[data-testid="stMetric"] {border-top:2px solid #A5BAAE;padding-top:12px;}
[data-testid="stSidebar"] {border-right:1px solid #CBD7CD;}
</style>""", unsafe_allow_html=True)

@st.cache_data
def read_json(name):
    return json.loads((DATA / name).read_text())

try:
    sample_portfolio = pd.read_csv(DATA / "synthetic_portfolio.csv")
    scenarios = load_scenarios()
    records = read_json("sample_news.json") + read_json("sample_social_posts.json")
except (OSError, ValueError) as exc:
    st.error(f"Could not load demo data: {exc}")
    st.stop()

with st.sidebar:
    st.markdown("### SIGNAL / SHOCK")
    st.caption("ANALYST WORKBENCH · v2.0")
    st.divider()
    st.markdown("**Portfolio source**")
    uploaded = st.file_uploader("Optional synthetic portfolio CSV", type="csv",
                                help="Use the bundled CSV as a schema template. No confidential data.")
    portfolio = sample_portfolio
    if uploaded:
        try:
            portfolio = pd.read_csv(uploaded)
            required = {"asset_id", "asset_name", "asset_type", "issuer", "market_value"}
            if not required.issubset(portfolio.columns):
                raise ValueError("Required columns: " + ", ".join(sorted(required)))
            if portfolio.asset_id.isna().any() or portfolio.asset_id.duplicated().any():
                raise ValueError("Each asset_id must be present and unique")
            stress_portfolio(portfolio, "Credit Event", 1, "validation only")
        except (ValueError, TypeError, KeyError) as exc:
            st.error(f"Invalid portfolio: {exc}")
            st.stop()
    st.metric("Portfolio value", f"${portfolio.market_value.sum():,.0f}")
    st.caption(f"{len(portfolio)} positions · USD · long-only")
    st.download_button("Download portfolio template", sample_portfolio.to_csv(index=False),
                       "synthetic_portfolio.csv", "text/csv")
    st.divider()
    st.markdown("**How to use this demo**")
    st.write("1. Inspect a headline.\n2. Review the event and issuer.\n3. Run a scenario and inspect the loss attribution.")
    st.caption("Runs locally after installation. No API keys or live feeds required.")

st.caption("S&P GLOBAL & CRISIL CAMPUS HACKATHON 2026 · DEVANSHI GUPTA, IGDTUW")
st.title("Signal-to-Shock")
st.markdown("#### Trace a financial headline to the exposures that matter.")
st.caption("Rule-based signals. Analyst-selected scenarios. Illustrative portfolio sensitivity.")
workbench, evidence, methodology = st.tabs(["Risk workbench", "Evidence & validation", "Method & assumptions"])

with workbench:
    left, right = st.columns([1.25, 1], gap="large")
    with left:
        st.subheader("01 / Inspect the signal")
        record = st.selectbox("Demo headline", records,
                             format_func=lambda r: f"{r['id']} · {r['company']}")
        text = st.text_area("Headline or social text", record["text"], height=130, key=f"text_{record['id']}")
        signal = analyze_text(text)
        st.markdown(f"**Detected event:** {signal['event_classification']}")
        a, b = st.columns(2)
        a.metric("Keyword sentiment", f"{signal['sentiment_score']:+.2f}")
        b.metric("Suggested intensity", f"{signal['impact_score']} / 10")
        if signal["review_required"]:
            st.warning("Review required: " + "; ".join(signal["review_reasons"]))
        with st.expander("Show matched words and decision rules"):
            st.json(signal["evidence"])
            st.caption("Scores do not express model confidence. Negation detection is only a warning heuristic.")
    with right:
        st.subheader("02 / Review the scenario")
        event = st.selectbox("Stress scenario", list(scenarios),
                            index=list(scenarios).index(signal["event_classification"]),
                            key=f"scenario_{record['id']}_{signal['event_classification']}")
        definition = scenarios[event]
        issuers = sorted(portfolio.issuer.dropna().unique())
        default_issuer = record.get("company")
        issuer = st.selectbox("Target issuer", issuers,
                              index=issuers.index(default_issuer) if default_issuer in issuers else 0,
                              key=f"issuer_{record['id']}", disabled=definition["scope"] != "issuer")
        intensity = st.slider("Stress intensity", 1, 10, signal["impact_score"],
                              key=f"intensity_{record['id']}_{signal['impact_score']}")
        st.caption(f"{definition['scope'].capitalize()} scope · base shocks × {intensity / 10:.1f}")
        with st.expander("Inspect the scenario assumptions"):
            st.dataframe(pd.DataFrame({"Asset type": list(definition["shocks"]),
                                       "Base shock (%)": [v*100 for v in definition["shocks"].values()]}),
                         hide_index=True, width="stretch")
            st.write("The analyst chooses the issuer. Editing the headline does not extract a new issuer.")
        reviewed = st.checkbox("I reviewed the ambiguous signal and selected the intended scenario",
                               key=f"review_{record['id']}_{text}_{event}") if signal["review_required"] else False
        run = st.button("Run portfolio stress test", type="primary", width="stretch",
                        disabled=not text.strip() or (signal["review_required"] and not reviewed))

    current_inputs = (text, event, intensity, issuer, portfolio.to_csv(index=False), reviewed)
    if run:
        try:
            report = build_report(text, portfolio, event, intensity, issuer, analyst_reviewed=reviewed)
            st.session_state["report"] = report
            st.session_state["report_inputs"] = current_inputs
        except (ValueError, KeyError, TypeError) as exc:
            st.error(str(exc))
    if "report" in st.session_state:
        if st.session_state["report_inputs"] != current_inputs:
            st.info("Inputs changed. Run the stress test again to refresh the results.")
        else:
            report = st.session_state["report"]
            summary = report["summary"]
            positions = pd.DataFrame(report["positions"])
            st.divider()
            st.subheader("03 / Explain the exposure")
            a, b, c, d = st.columns(4)
            a.metric("Simulated P&L", f"${summary['pnl']:,.0f}", f"{summary['pnl_pct']:+.2f}%")
            b.metric("Stressed value", f"${summary['portfolio_after']:,.0f}")
            c.metric("Eligible exposure", f"${summary['eligible_exposure']:,.0f}")
            d.metric("Positions with a shock", f"{summary['shocked_positions']} / {len(positions)}")
            for warning in report["warnings"]:
                st.warning(warning)
            loss, curve = st.columns([1.2, 1], gap="large")
            with loss:
                st.markdown("**Position contribution to P&L (USD)**")
                st.bar_chart(positions.set_index("asset_name")[["pnl"]], color="#C66A4A", horizontal=True)
            with curve:
                st.markdown("**Sensitivity to intensity**")
                st.line_chart(sensitivity(portfolio, event, issuer).set_index("Intensity"), color="#285B4A")
                st.caption("A deterministic sensitivity curve. It is not a loss distribution or confidence interval.")
            if definition["scope"] == "issuer":
                st.info(f"Scope matters: applying these same shocks to every issuer gives USD {summary['naive_all_issuer_pnl']:,.0f}. "
                        f"Issuer filtering changes P&L by USD {summary['scope_difference']:,.0f}. This compares assumptions, not forecast accuracy.")
            with st.expander("Position ledger and calculation", expanded=True):
                st.caption("P&L = market value × base shock × intensity / 10 × issuer eligibility")
                st.dataframe(positions[["asset_name", "issuer", "market_value", "affected", "shock_pct", "pnl", "value_after"]].round(4),
                             hide_index=True, width="stretch")
            with st.expander("Compare all scenarios at the same intensity"):
                st.caption(f"Issuer scenarios target {issuer}. Systemic scenarios cover all positions. Scenarios are alternatives, not additive.")
                st.dataframe(scenario_comparison(portfolio, intensity, issuer), hide_index=True, width="stretch")
            a, b = st.columns(2)
            a.download_button("Download complete audit report (JSON)", json.dumps(report, indent=2, allow_nan=False),
                              f"audit_{report['run_id']}.json", "application/json")
            b.download_button("Download position ledger (CSV)", positions.to_csv(index=False),
                              f"positions_{report['run_id']}.csv", "text/csv")
            st.caption(f"Run {report['run_id']} · Includes input text, portfolio, scenario assumptions, rule evidence and SHA-256 input fingerprint.")
    else:
        st.info("Select a headline and run a stress test to see position-level attribution.")

with evidence:
    st.subheader("Measured evidence, with its limits")
    metrics = json.loads((ROOT / "results/real_data/metrics.json").read_text())
    majority = 2146 / 3453
    a, b, c = st.columns(3)
    a.metric("Sentiment accuracy", f"{metrics['accuracy']:.2%}", f"{(metrics['accuracy']-majority)*100:.2f} pp vs always-neutral")
    b.metric("Macro F1", f"{metrics['macro_f1']:.4f}")
    c.metric("Negative recall", f"{metrics['classification_report']['negative']['recall']:.2%}")
    st.warning("The baseline misses most negative examples. All scenario decisions require analyst judgment.")
    st.write("Financial PhraseBank, sentences_75agree: 3,453 labelled sentences. The recorded evaluation uses the unchanged sentiment rule. Event classification and loss prediction are not validated by these metrics.")
    cm = metrics["confusion_matrix"]
    st.markdown("**Confusion matrix: rows = actual, columns = predicted**")
    st.dataframe(pd.DataFrame(cm["matrix"], index=cm["labels"], columns=cm["labels"]), width="stretch")
    st.subheader("Historical context")
    st.dataframe(pd.read_csv(ROOT / "results/market_data/event_returns.csv")[["event_name", "ticker", "ticker_return_pct", "benchmark_return_pct"]], hide_index=True, width="stretch")
    st.caption("Selected T−1 to T+5 windows. Descriptive returns, not causal effects or calibration of scenario shocks. Cached inputs support offline reproduction.")
    st.markdown("[Financial PhraseBank source](https://huggingface.co/datasets/takala/financial_phrasebank)")

with methodology:
    st.subheader("A transparent decision-support workflow")
    st.image(str(ROOT / "docs/architecture.png"), caption="Text evidence, analyst review, scenario engine and an auditable output")
    st.markdown("""
**Rules:** keyword counts determine sentiment. First matching category determines the suggested event.
Multiple categories or possible negation trigger review. The analyst can override the scenario.

**Scenario engine:** issuer events affect the selected issuer only. Systemic events affect all positions.
Intensity scales each configured shock linearly. Positive and negative outcomes are both possible.

**Domain limits:** this is a USD, long-only sensitivity prototype. Bonds and swaps receive simplified
market-value haircuts. There is no duration, spread, DV01, margin, liquidity or contagion model.
A zero loss is not evidence of safety. Social posts are unverified synthetic examples.

**Data:** all demo headlines and portfolio positions are synthetic. Research metrics use public sources.
No trained model, live news feed or production deployment is claimed.
""")
st.divider()
st.caption("DEVANSHI GUPTA · IGDTUW · Synthetic demonstration / illustrative assumptions / analyst review required")
