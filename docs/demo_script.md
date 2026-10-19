# Demo recording guide

Target duration: **9:30**, leaving a margin below ten minutes. Record the real application with your own narration. Rehearse once, keep text readable, and avoid notifications or unrelated browser tabs. This script is preparation, not a completed video.

| Time | Screen/action | Narration and point |
|---|---|---|
| 0:00–0:30 | Title slide | “I’m Devanshi Gupta from IGDTUW. Signal-to-Shock helps an analyst connect a financial headline to the portfolio positions affected by an explicit scenario.” |
| 0:30–1:00 | README quickstart and terminal | Show the environment activation and `python -m streamlit run app.py`. Dependencies can be installed before recording. Mention the demo runs offline without API keys. |
| 1:00–1:45 | Workbench, NEWS-002 | Read the bank-default headline. Show default/liquidity evidence and the negative keyword score. Explain that these are transparent rules, not a trained model. |
| 1:45–2:30 | Scenario controls | Select Credit Event, Example Bank Ltd, intensity 9. Expand shocks. Explain issuer scope and intensity divided by ten. The issuer is analyst-selected. |
| 2:30–3:30 | Run and inspect results | “Three bank positions are shocked. The assumed loss is $62,550, or 5.44% of this $1.15 million synthetic portfolio.” Show $1,087,450 after stress and the individual losses: equity $21,600, loan $33,750, swap $7,200. |
| 3:30–4:15 | Charts and scope comparison | Explain the linear intensity curve. Point out the $121,050 counterfactual if unrelated issuers also receive the shocks. “The $58,500 difference is due to scope assumptions; it is not a proven avoided loss.” |
| 4:15–5:00 | Scenario comparison and export | Expand all scenarios. Explain that these are alternative assumptions, not additive events. Download the JSON and CSV. Open the JSON to show input text, scenario definition, positions and fingerprint. |
| 5:00–5:45 | NEWS-005, negation example | Show “denies default” / “no liquidity crisis”. The rule still matches keywords; review blocks a run until explicitly confirmed. Explain that negation flags are incomplete and analyst judgment remains necessary. |
| 5:45–6:30 | NEWS-003, macro event | Run the systemic example. Show all positions are eligible. Change intensity and rerun to demonstrate how assumptions change outputs. |
| 6:30–7:30 | Evidence tab | “On 3,453 Financial PhraseBank sentences, current keyword rules reach 67.33% accuracy and 0.4319 macro F1. Always-neutral reaches 62.15% accuracy. Negative recall is only 9.52%, so this is not an autonomous decision system.” |
| 7:30–8:00 | Historical table | Describe the three selected event windows. Say XLF is a broad US financial proxy. “These observed returns do not prove causation or calibrate our shocks.” |
| 8:00–8:40 | Method tab / architecture | Trace input, evidence, analyst review, stress engine and audit output. Explain why the components are separate and testable. |
| 8:40–9:10 | Terminal | Run `python -m pytest -q` and `python scripts/reproduce.py`. Explain that tests check calculation consistency and UI behavior, not real financial prediction quality. |
| 9:10–9:30 | Final slide | State the main limitations and next experiments: contextual NLP comparison, held-out event calibration, duration/DV01 repricing. Close on the value of traceable analyst discussion. |

## Before uploading

- Watch the complete recording, including the beginning and end. Verify readable labels and narration.
- Upload to YouTube as **Unlisted**. The video must be playable while signed out; do not substitute a cloud-drive link.
- Add the real URL to the README's Demo Video Link field.
- Run `python scripts/check_submission.py --strict`, then commit and push the README.
- Verify public repository/deck access and video playback in a private browser window.
- Submit repository, demo and deck through the official form before the communicated deadline. Save the submission acknowledgement.
