import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.nlp.analyzer import analyze_text
from src.risk.stress import stress_portfolio

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"

SOURCE_FILES = {
    "Financial news": "sample_news.json",
    "Social-media posts": "sample_social_posts.json",
}


def load_records(filename):
    with (DATA / filename).open(encoding="utf-8") as file:
        records = json.load(file)
    if not isinstance(records, list):
        raise ValueError(f"{filename} must contain a JSON list")
    return records


st.set_page_config(page_title="Signal-to-Shock", layout="wide")
st.title("Signal-to-Shock")
st.caption(
    "Financial event intelligence and portfolio stress testing | "
    "Synthetic-data prototype"
)

source = st.selectbox("Input source", list(SOURCE_FILES))
records = load_records(SOURCE_FILES[source])

record = st.selectbox(
    "Select a sample record",
    records,
    format_func=lambda r: f"{r['id']} — {r['company']}",
)

text = st.text_area("Text to analyze", value=record["text"], height=120)
portfolio = pd.read_csv(DATA / "synthetic_portfolio.csv")

left, right = st.columns(2)
left.metric("Starting portfolio value", f"${portfolio['market_value'].sum():,.2f}")
right.metric("Input source", source)

if st.button("Analyze event", type="primary"):
    signal = analyze_text(text)

    st.subheader("Structured risk signal")
    c1, c2, c3 = st.columns(3)
    c1.metric("Sentiment", f"{signal['sentiment_score']:+.3f}")
    c2.metric("Event", signal["event_classification"])
    c3.metric("Impact score", f"{signal['impact_score']}/10")
    st.json({
        "record_id": record["id"],
        "company": record["company"],
        "source": record["source"],
        **signal,
    })

    if signal["impact_score"] > 7:
        stressed = stress_portfolio(
            portfolio,
            signal["event_classification"],
            signal["impact_score"],
        )
        before = stressed["market_value"].sum()
        after = stressed["value_after"].sum()

        st.subheader("Portfolio stress test")
        a, b, c = st.columns(3)
        a.metric("Before", f"${before:,.2f}")
        b.metric("After", f"${after:,.2f}")
        c.metric("Simulated P&L", f"${after - before:,.2f}")

        st.dataframe(stressed, use_container_width=True, hide_index=True)
        st.bar_chart(stressed.set_index("asset_name")["pnl"])
    else:
        st.info("The configured impact threshold was not exceeded.")

    output_dir = DATA / "outputs"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "latest_signal.json").write_text(
        json.dumps(signal, indent=2), encoding="utf-8"
    )

st.caption(
    "The keyword model and scenario shocks are illustrative. "
    "They are not calibrated market forecasts or investment advice."
)
