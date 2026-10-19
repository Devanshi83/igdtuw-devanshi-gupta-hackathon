# Validation record

Validation date: 19 October 2026. Local platform: macOS arm64, Python 3.12.

## Completed checks

- A fresh isolated Python environment installed `requirements-dev.txt` successfully from package distributions.
- `python -m pytest -q`: **52 passed**, including Streamlit AppTest end-to-end execution, persistent results, stale-input suppression, manual bank-loss reconciliation, replayable audit inputs, ambiguity review, unsupported asset rejection, non-finite values, scenario sensitivity and partial market-window rejection.
- `python -m pip check`: **No broken requirements found**.
- `python scripts/reproduce.py`: **bank-credit P&L −$62,550**, all **three complete historical windows** reproduced offline.
- The current sentiment rule was rerun on **3,453 retained labelled sentences**. Accuracy **67.33%**, macro F1 **0.4319**, negative recall **9.52%**. Source and input fingerprints are in the aggregate metric artifact.
- Browser verification of the actual Streamlit bank-credit workflow confirmed displayed totals, charts, scope comparison and ledger. `docs/workbench.png` is an actual application screenshot.
- Seven-slide PPTX passed package, layout/font and import checks. All rendered slides were visually inspected. PDF export was rendered and inspected separately.

The online Financial PhraseBank acquisition was not rerun; current evaluation used the retained labelled CSV. Its licensed text is excluded from Git. Fresh historical vendor retrieval was not needed; cached inputs were used.

## Boundaries

Tests establish software consistency, not real-world predictive validity. The recorded public-data sentiment test is not a test of event extraction, calibrated shock magnitudes or financial loss prediction. No latency benchmark, analyst study, live deployment or measured productivity gain is claimed.

Package checks can verify required files, README local links and input checksums. A strict check rejects the absent YouTube URL. The actual video upload/playback, official deadline, original case brief and final form submission remain external steps.
