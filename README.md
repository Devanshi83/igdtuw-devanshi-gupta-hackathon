# Signal-to-Shock — S&P Global & CRISIL Campus Hackathon 2026

**Candidate Name:** Devanshi Gupta
**College Email ID:** Pending — add your official college email before submission.
**College / Campus:** Indira Gandhi Delhi Technical University for Women (IGDTUW)
**Demo Video Link:** Pending — add the public YouTube URL after uploading the unlisted demo.
**Slide Deck Link:** docs/presentation.pdf

## 1. Project Overview

Signal-to-Shock is a financial event intelligence prototype that converts unstructured financial text into structured risk signals and demonstrates how major events could affect a synthetic portfolio.

The application provides a Streamlit interface for selecting synthetic financial news or social-media text, which is then processed through the following workflow:
- **Keyword-based sentiment analysis** (rule-based; not a trained language model).
- **Rule-based event classification and impact scoring.**
- **Scenario-driven portfolio stress testing** (illustrative shocks, not calibrated market forecasts).

The system displays the generated structured signals, before/after portfolio values, simulated P&L, and affected positions. It distinguishes between issuer-specific scenarios (which affect only positions matching the target issuer) and systemic scenarios (which affect all positions).

## 2. Architecture & Implementation Details

The project is implemented in Python and Streamlit, with modular components:
- `app.py`: The main Streamlit interface for the application.
- `src/nlp/analyzer.py`: Implements the keyword-based sentiment analysis and rule-based event classification.
- `src/risk/stress.py`: Handles scenario-driven portfolio stress testing.
- `data/scenarios.json`: Contains the definitions for base shocks and scenario scopes (issuer vs. systemic).
- `data/`: Contains the synthetic dataset, including portfolio and sample text files.
- `tests/test_risk_engine.py`: Unit tests for the NLP and risk engine components.
- `.github/workflows/tests.yml`: GitHub Actions workflow for continuous integration.

The architecture diagram is available at [`docs/architecture.png`](docs/architecture.png).

### Methodology

- **Sentiment Calculation**: The sentiment score is calculated using the formula `(positive_count - negative_count) / (positive_count + negative_count)`. **Note:** The analyzer is a keyword baseline, not a trained language model.
- **Scenario-Shock Calculation**: The stressed portfolio values are calculated by applying shocks to the market value. The simulated value is calculated as: `market_value * (1 + (base_shock_pct * (impact_score / 10.0) * affected))`. **Note:** These shocks are illustrative assumptions, not calibrated market forecasts or investment advice.

## 3. Dataset

The project uses a fully synthetic dataset for demonstration purposes. The initial synthetic portfolio consists of six positions totaling $1,150,000 across Equity, Bond, Loan, and Derivative asset types. Additional synthetic news and social-media fixtures are located in the `data/` directory.

## 4. Quickstart & Installation

To run this project locally, ensure you have Python 3.12 installed.

```sh
git clone https://github.com/Devanshi83/igdtuw-devanshi-gupta-hackathon.git
cd igdtuw-devanshi-gupta-hackathon
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```

To run the test suite locally:
```sh
python -m pytest -q
```

## 5. Real-Data Evaluation

Two separate evaluations were conducted on real-world data. These evaluate the existing rule-based components without retraining or tuning.

### Sentiment Evaluation (Financial PhraseBank)

The rule-based sentiment analyzer was evaluated on 3,453 labelled financial-news sentences from the [Financial PhraseBank](https://huggingface.co/datasets/takala/financial_phrasebank) (sentences_75agree, CC BY-NC-SA 3.0). The raw dataset is dynamically downloaded via the Hugging Face `datasets` library and is **not redistributed** in this repository.

- **Accuracy:** 67.30%
- **Macro F1:** 0.4314

Full methodology, per-class metrics, confusion matrix, and limitations: [`docs/real_data_evaluation.md`](docs/real_data_evaluation.md).

### Historical Market-Data Analysis

Historical daily prices for three documented financial events were retrieved via `yfinance` and analysed with a T-1 to T+5 trading-day window against an SPY benchmark.

| Event | Ticker | Return | SPY Return | Excess |
|-------|--------|--------|------------|--------|
| SVB Collapse (2023-03-09) | KRE | -19.91% | -0.70% | -19.21% |
| Credit Suisse Crisis (2023-03-15) | XLF | -2.77% | +0.48% | -3.25% |
| UK Mini-Budget (2022-09-23) | EWU | -5.52% | -4.55% | -0.96% |

These are observed historical returns, not causal proof or validation of our portfolio shock percentages. Full details: [`docs/market_data_analysis.md`](docs/market_data_analysis.md).

## 6. Testing Status

The test suite covers the NLP analyzer, risk engine, sentiment evaluation logic, and market-data return calculations. Continuous integration is configured in `.github/workflows/tests.yml`.

## 7. Limitations

- The NLP engine relies on simple keyword matching rather than contextual language models (like LLMs or transformers).
- The stress testing impacts and base shock percentages are purely illustrative and do not reflect real market dynamics.
- The portfolio and input texts are synthetic and do not reflect actual financial data or events.
- The Financial PhraseBank evaluation measures only sentiment extraction accuracy; it does not validate event classification, impact scoring, or portfolio stress assumptions.
- Historical market returns show correlation, not causation, and do not validate the synthetic shock magnitudes.

## Demo Video

Pending — the unlisted YouTube link will be added after the recording is uploaded and verified.

## Presentation

See docs/presentation.pdf when available.
