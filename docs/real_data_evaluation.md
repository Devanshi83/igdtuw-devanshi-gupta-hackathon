# Sentiment evaluation

## Source and scope

Financial PhraseBank, Malo et al. (2014), [dataset card](https://huggingface.co/datasets/takala/financial_phrasebank), configuration `sentences_75agree`, CC BY-NC-SA 3.0. There are 3,453 human-labelled sentences. This evaluates **sentiment only**, not event classification, intensity or loss prediction. There is no trained model or tuning against these labels in this revision.

## Current reproducible results

On 19 October 2026 the current analyzer was rerun against retained local labelled input. Accuracy: **67.33%**. Macro F1: **0.4319**. Always-neutral comparator: **62.15%**, macro F1 **0.2555**. See `results/real_data/metrics.json` for complete precision, source/input SHA-256 and version provenance.

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Negative | 45.98% | 9.52% | 0.1578 | 420 |
| Neutral | 69.31% | 96.83% | 0.8079 | 2146 |
| Positive | 56.25% | 23.34% | 0.3299 | 887 |

Confusion matrix (rows actual, columns predicted):

| Actual / predicted | Negative | Neutral | Positive |
|---|---:|---:|---:|
| Negative | 40 | 279 | 101 |
| Neutral | 8 | 2078 | 60 |
| Positive | 39 | 641 | 207 |

The model predicts neutral too often and misses most negative sentences. Do not present accuracy as evidence of reliable adverse-event detection. A contextual model is a future measured comparison, not a proven improvement.

## Revision note

The earlier saved metrics were 67.30% accuracy and 0.4314 macro F1. Running the current source against the retained labels differs on one prediction. Current values supersede the old report. This small discrepancy is not presented as a substantive performance improvement. The sentiment rule itself was not changed during this work; added evidence/review flags do not change its score.

## Reproduction

```bash
python -m pip install -r requirements-research.txt
python scripts/evaluation/evaluate_sentiment.py
# Alternatively, with legally obtained retained input:
python scripts/evaluation/evaluate_sentiment.py --input-csv /path/to/labelled.csv
```

CSV schema: `text,true_label`. Labels: negative, neutral, positive. The current run used the retained local labelled CSV. A fresh online dataset acquisition was not rerun in this revision and depends on external availability and the legacy Hugging Face dataset loader. The dashboard does not need these research dependencies.

Only aggregate outputs are committed. Raw labelled sentences, predictions and misclassification examples remain excluded from Git and retain their source license. The input hash allows comparison with the same canonical text/label input without redistributing it.
