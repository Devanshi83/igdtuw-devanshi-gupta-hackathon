# Signal-to-Shock — S&P Global & CRISIL Campus Hackathon 2026

**Candidate Name:** Devanshi Gupta
**College Email ID:** [Placeholder - to be supplied]
**College / Campus:** Indira Gandhi Delhi Technical University for Women (IGDTUW)
**Demo Video Link:** Pending
**Slide Deck Link:** docs/presentation.pdf

## 1. Project Overview

Signal-to-Shock is a financial event intelligence prototype that converts unstructured financial text into structured risk signals and demonstrates how major events could affect a synthetic portfolio.

The application provides a Streamlit interface for selecting synthetic financial news or social-media text, which is then processed through the following workflow:
- **Keyword-based sentiment analysis.**
- **Rule-based event classification and impact scoring.**
- **Scenario-driven portfolio stress testing.**

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

An architecture diagram is available at docs/architecture.png.

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

## 5. Testing Status

Currently, 12 tests pass locally. For the latest continuous integration results, please refer to the GitHub Actions workflow runs in the repository.

## 6. Limitations

- The NLP engine relies on simple keyword matching rather than contextual language models (like LLMs or transformers).
- The stress testing impacts and base shock percentages are purely illustrative and do not reflect real market dynamics.
- The portfolio and input texts are synthetic and do not reflect actual financial data or events.

## Demo Video

Pending.

## Presentation

See docs/presentation.pdf when available.
