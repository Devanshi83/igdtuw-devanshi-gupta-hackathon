# Signal-to-Shock — Evaluation Report

## 1. Purpose

This report records deterministic checks of the current Signal-to-Shock
implementation. The evaluation covers event classification, sentiment and
impact-rule consistency, and portfolio stress calculations.

The checks use hand-authored examples and configured scenario assumptions.
They are not a validation of real-world financial-news accuracy or
market-risk prediction.

## 2. Evaluation setup

The project uses a keyword-based NLP baseline. Event categories are selected
through configured keyword rules. Sentiment is calculated from positive and
negative keyword counts. Impact scores use category-specific severity values
and an additional increment when at least three negative keywords are found,
subject to the implementation's cap.

Portfolio evaluation compares calculated outputs against independently
specified expected values derived from the configured scenario shocks.

Evaluation scripts:

- `scripts/evaluate_analyzer.py`
- `scripts/evaluate_sentiment_impact.py`
- `scripts/evaluate_portfolio.py`
- `scripts/run_evaluation.sh`

## 3. Event classification

The hand-authored classification set contains 28 examples across six labels.

| Category | Correct | Total |
|---|---:|---:|
| Credit Event | 4 | 4 |
| Geopolitical | 5 | 5 |
| Macroeconomic | 4 | 4 |
| Merger/Acquisition | 5 | 5 |
| Other | 5 | 5 |
| Product/Cyber Event | 5 | 5 |
| **Total** | **28** | **28** |

Observed agreement with the expected labels: **28/28 (100%)**.

During evaluation, the sentence "New sanctions were announced against the
region." was initially classified as `Other`. The geopolitical keyword rule
was updated to recognize both `sanction` and `sanctions`, and a regression
test was added. The evaluation then reported no mismatches.

This result applies only to the small, hand-authored test set. It must not be
presented as real-world classification accuracy.

## 4. Sentiment and impact consistency

Eight hand-authored cases checked expected sentiment patterns and consistency
with the configured impact rules.

- Sentiment pattern checks: **8/8 passed**.
- Impact rule checks: **8/8 passed**.

These checks verify behavior against simple expectations and the existing
implementation. They do not establish sentiment quality, calibrated event
severity, or real-world financial impact.

## 5. Portfolio stress calculations

The numerical evaluation checked four scenarios at impact intensity 9/10.

| Scenario | Expected P&L | Expected affected positions | Result |
|---|---:|---:|---|
| Systemic Macroeconomic | -$63,000 | 6 | Passed |
| Credit Event for Example Technology Ltd | -$40,500 | 2 | Passed |
| Credit Event for nonexistent issuer | $0 | 0 | Passed |
| Merger/Acquisition for Example Technology Ltd | +$4,500 | 2 | Passed |

All **40/40 numerical checks passed**, covering starting and ending portfolio
values, total P&L, affected-position counts, and position-level P&L.

The expected values are calculated from the project's configured shocks and
synthetic portfolio. They are not observed market outcomes or forecasts.

## 6. Automated tests

The latest recorded automated test run reported:

- **32 passed**
- Runtime: **0.36 seconds**

The test suite includes NLP behavior, scenario validation, issuer matching,
portfolio calculations, and the regression test for plural "sanctions".

## 7. Limitations

1. The NLP analyzer is a keyword-based baseline, not a trained language model.
2. The classification examples are hand-authored and are not an independent
   or representative financial-news benchmark.
3. Keyword sentiment does not fully handle negation, context, sarcasm, or
   nuanced financial language.
4. Impact scores and scenario shock percentages are configured assumptions;
   they have not been calibrated against historical market events.
5. Portfolio stress results demonstrate calculation consistency on synthetic
   data, not predictive validity or investment advice.
6. The reported results do not establish generalization to unseen news,
   real portfolios, or live market conditions.

## 8. Reproduction

From the repository root, with project dependencies installed:

```bash
./scripts/run_evaluation.sh
```

Individual scripts can also be run using the Python environment configured
for the project. If imports cannot resolve from a local environment, run
the scripts with the repository root on `PYTHONPATH`.

## 9. Conclusion

The tested examples matched their expected classification labels after the
plural-keyword fix. Sentiment and impact checks followed the implemented
rules, and the four portfolio scenarios matched their specified expected
values.

Further validation on independently labeled financial news and justified
risk scenarios is required before making claims about real-world accuracy
or financial predictive performance.
