# Evaluation guide

Current evidence lives in:
- [Sentiment evaluation](real_data_evaluation.md): public labels, current source fingerprint and class-level metrics.
- [Historical market analysis](market_data_analysis.md): three complete cached T−1 to T+5 windows.
- [Validation record](validation.md): fresh install and software regression checks.
- [Bank scenario audit](../results/demo/bank_credit_audit.json): independently checked position arithmetic.

The older scripts evaluate_analyzer.py, evaluate_portfolio.py and evaluate_sentiment_impact.py are small **synthetic smoke checks**, not an unbiased estimate of real-world NLP or financial performance. Matching handcrafted expected outputs must not be marketed as predictive accuracy. The supported regression suite is `python -m pytest -q`.
