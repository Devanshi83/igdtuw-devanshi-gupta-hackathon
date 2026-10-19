# Methodology and domain interpretation

The application is a sensitivity workbench. Its causal chain is an **analyst assumption**, not an estimated economic model.

1. Tokenize text and count positive/negative keywords. Preserve the baseline rule for comparability.
2. Match event categories with word boundaries. Keep the first match as a suggestion, but expose all matches. Flag multiple categories, absent event evidence, and common negation terms for explicit review.
3. The analyst chooses an issuer independently of the text, a scenario and intensity. The interface does not perform entity recognition. A matching fictional company name in a sample supplies only a convenient default.
4. Apply `market_value × base_shock × intensity / 10` to eligible positions. Issuer eligibility uses exact case-insensitive, whitespace-trimmed names. Systemic eligibility covers the whole portfolio. Eligible positions can have zero configured shock; report these separately from shocked positions.
5. Reconcile total P&L to position P&L. Persist the displayed analysis across reruns but suppress it when inputs change. Export the complete input/scenario snapshot and output.

## Scope comparison

The naive counterfactual uses the same shocks and intensity on every issuer. The bank-credit example produces −$62,550 with scope and −$121,050 without scope. The $58,500 difference demonstrates how assumptions change results. It is not actual prevented loss, an improved forecast or a measured efficiency gain.

## Limitations

A phrase containing “no default” still matches “default”; the UI flags it and requires analyst confirmation rather than claiming to understand it. Some negations, sarcasm and ambiguous statements will evade the heuristic. Review also applies to the generic Other scenario, whose shocks are an explicit hypothetical assumption. Positive sentiment does not automatically imply positive portfolio P&L.

The swap is represented by a positive market value and a haircut, not notional or DV01. Bonds omit duration, convexity and credit-spread sensitivity. A common asset-type shock ignores sector, maturity, currency, nonlinear repricing and hedges. There are no probability estimates, confidence intervals, VaR, backtesting or causal loss claims. A proper risk system would require instrument risk factors, calibrated scenarios, data quality controls and governance.

The audit SHA-256 detects changed canonical inputs, including the scenario definition, selected controls and model-version tag. It does not authenticate a report's author. Reports contain their inputs; only use synthetic/public text and portfolios for the demo.
