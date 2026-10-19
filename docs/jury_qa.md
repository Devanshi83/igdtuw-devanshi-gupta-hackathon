# Jury preparation

## Opening (about 30 seconds)

“Signal-to-Shock addresses the gap between a headline and a portfolio discussion. It shows the text evidence, lets an analyst select the scenario and issuer, and calculates an attributable what-if result. In our synthetic bank-default example, issuer scope produces a $62,550 loss across three positions; applying the same shocks to every issuer produces $121,050. Every input and assumption is exportable. The novelty is a reviewable workflow, not a claim to predict losses from text.”

## Questions to be ready for

**Why use rules instead of an LLM?**

Rules make the baseline cheap, offline and inspectable. Their limitation is measured: negative recall is 9.52%. A contextual model is a next comparison experiment, requiring a frozen holdout and evaluation of errors, latency and explainability. Do not say it will definitely outperform before measuring.

**What was trained?**

Nothing. Keyword lists, event order, intensity defaults and shock tables are explicit rules/assumptions. Financial PhraseBank evaluates sentiment only. No labelled evaluation examples were used to tune the rules during this revision.

**What makes this different from a sentiment dashboard?**

Issuer filtering, instrument-level attribution, explicit scenario overrides, ambiguity review, comparable what-if scenarios and a complete downloadable audit. Show the code and bank example rather than claiming market novelty you have not researched.

**Where does $62,550 come from?**

Bank equity: $200,000 × −12% × 0.9 = −$21,600. Bank loan: $250,000 × −15% × 0.9 = −$33,750. Swap: $100,000 × −8% × 0.9 = −$7,200. Sum = −$62,550. The other issuer and sovereign positions remain unchanged.

**Does intensity 9 mean a 90% chance of loss?**

No. It scales the configured shock magnitude to 90%. There are no event probabilities or confidence intervals. The sensitivity chart is linear because the model is linear.

**Does the historical event study prove your shock assumptions?**

No. It describes three preselected windows with many confounders. SPY is a broad comparator. XLF is US financials, not Credit Suisse stock. Calibrating and testing shocks would require a broader event dataset, specified exposure mappings, and time-separated evaluation.

**Why is 67.33% sentiment accuracy not enough?**

Class imbalance. Always predicting neutral already yields 62.15%. Macro F1 is 0.4319; negative recall is only 9.52%. Show the confusion matrix. Accuracy alone hides missed adverse text.

**Why did older documents say 67.30%?**

The current source was rerun on retained labelled data and one prediction differed from the older saved report. The repo records current aggregate results, source/input fingerprints and the revision note. No uplift claim is based on this tiny difference.

**Can the system understand “no default”?**

No. The keyword matches remain, and a heuristic negation flag prompts explicit review. The heuristic misses some language. Demonstrate this honestly with NEWS-005.

**Why use issuer selection instead of entity extraction?**

To make the exposure assumption explicit. Automatic entity resolution would need aliases, identifiers, subsidiaries and confidence/review rules. The sample supplies a convenient default; editing text does not identify a new company automatically.

**Are the swap and bond calculations financially realistic?**

They are simplified market-value sensitivities. A swap needs signed DV01/curve exposures, cashflows and counterparty treatment; a bond needs duration, spread and convexity. Market value is not notional. These missing inputs are documented, not inferred.

**Can this model a bank-run contagion?**

Only as a manually chosen systemic what-if. It does not infer second-round contagion or a network of counterparty exposures.

**What does the audit fingerprint prove?**

Identical canonical inputs/settings generate the same hash and run ID. The report contains the scenario definition and position results. It does not authenticate the author or make the assumptions correct.

**What fails safely?**

Empty input is blocked. Unsupported assets and non-finite/negative market values are rejected. Unmatched issuers produce a warning. Incomplete historical windows are rejected. Changed controls suppress stale results until rerun.

**How would you measure business impact next?**

Run a controlled analyst task study comparing manual mapping with the workbench: time to a reviewed report, incorrect issuer assignments, reproducibility, and usefulness ratings. No such user study has been conducted yet.

**Did you use AI?**

Yes, for implementation, tests, documentation and slide preparation. This is an individual submission. Be prepared to explain every formula, function and limitation. Do not claim unaided authorship.

## Rehearsal exercise

Without reading notes, reproduce the bank calculation, explain the confusion matrix, run a negated headline and locate the scenario configuration. Then explain why a passing test suite does not prove predictive risk accuracy.
