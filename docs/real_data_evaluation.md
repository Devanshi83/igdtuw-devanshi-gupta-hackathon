# Real Data Evaluation

This document describes the evaluation of the existing rule-based sentiment analyser on a real-world, human-labelled financial news dataset.

## Dataset Details
- **Source**: [Financial PhraseBank](https://huggingface.co/datasets/takala/financial_phrasebank)
- **Configuration**: `sentences_75agree`
- **Expected Size**: 3,453 sentences
- **Labels**: negative, neutral, positive
- **Licence**: CC BY-NC-SA 3.0. We preserve attribution to the original authors. The dataset is used strictly for non-commercial evaluation. The raw dataset is dynamically downloaded using the Hugging Face `datasets` library and is not redistributed in this repository.

*Note: This dataset represents historical financial-news sentences. It does not reflect current news or live market events.*

## Setup and Reproducibility

To run the evaluation:
1. Ensure dependencies are installed from `requirements.txt`.
2. Run the evaluation script:
   ```sh
   python scripts/evaluation/evaluate_sentiment.py
   ```
3. Predictions are saved to `results/real_data/predictions.csv`.
4. Metrics are saved to `results/real_data/metrics.json`.

## Methodology
The existing analyzer (`src/nlp/analyzer.py`) was evaluated against the dataset without any tuning or modifications.
The analyzer returns a sentiment score between -1.0 and 1.0. This score is mapped to discrete labels as follows:
- `score > 0` => `positive`
- `score < 0` => `negative`
- `score == 0` => `neutral`

**Important Distinction**: This evaluates *only* the sentiment extraction. It does not validate the event classification, impact scoring, or the subsequent portfolio stress testing assumptions.

## Results
- **Total Records**: 3453
- **Overall Accuracy**: 67.30%
- **Macro F1-Score**: 0.4314

### Per-Class Metrics
- **Negative**: Precision 45.98%, Recall 9.52%, F1-Score 0.1578
- **Neutral**: Precision 69.29%, Recall 96.83%, F1-Score 0.8078
- **Positive**: Precision 56.13%, Recall 23.22%, F1-Score 0.3285

### Confusion Matrix (Negative, Neutral, Positive)
| True \ Predicted | Negative | Neutral | Positive |
|-----------------|----------|---------|----------|
| **Negative**    | 40       | 279     | 101      |
| **Neutral**     | 8        | 2078    | 60       |
| **Positive**    | 39       | 642     | 206      |

## Limitations & Misclassifications
The baseline rule-based analyzer heavily misclassifies both positive and negative sentences as "neutral". This occurs because it relies entirely on a fixed list of keywords (e.g., "profit", "surge", "loss"). It misses domain-specific context, percentages, or complex phrasing. For example:

- *"With the new production plant the company would increase its capacity to meet the expected increase in demand and would improve the use of raw materials and therefore increase the production profitability ."* (True: positive, Pred: neutral)
- *"Consolidated net sales increased 16 % to reach EUR74 .8 m , while operating profit amounted to EUR0 .9 m compared to a loss of EUR0 .7 m in the prior year period ."* (True: positive, Pred: neutral)

Because it doesn't recognize phrases like "increased 16 %" or "improve the use", the rule-based approach defaults to neutral. Contextual language models (like LLMs or FinBERT) would perform significantly better on this task.
