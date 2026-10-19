import json
import logging
from pathlib import Path

import pandas as pd
from datasets import load_dataset
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)

# Add src to path so we can import
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.nlp.analyzer import analyze_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "results" / "real_data"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def map_score_to_label(score):
    if score > 0:
        return "positive"
    elif score < 0:
        return "negative"
    else:
        return "neutral"

def run_evaluation():
    logger.info("Loading dataset...")
    # financial_phrasebank labels: 0=negative, 1=neutral, 2=positive
    LABEL_MAP = {0: "negative", 1: "neutral", 2: "positive"}
    dataset = load_dataset("financial_phrasebank", "sentences_75agree", split="train", trust_remote_code=True)
    logger.info(f"Loaded {len(dataset)} records.")
    results = []
    for row in dataset:
        text = row["sentence"]
        true_label_idx = row["label"]
        true_label = LABEL_MAP[true_label_idx]
        
        # Run our analyzer
        signal = analyze_text(text)
        pred_label = map_score_to_label(signal["sentiment_score"])
        
        results.append({
            "text": text,
            "true_label": true_label,
            "pred_label": pred_label,
            "sentiment_score": signal["sentiment_score"],
            "event_classification": signal["event_classification"]
        })
        
    df = pd.DataFrame(results)
    
    # Save predictions
    df.to_csv(RESULTS_DIR / "predictions.csv", index=False)
    
    # Metrics
    y_true = df["true_label"]
    y_pred = df["pred_label"]
    
    acc = accuracy_score(y_true, y_pred)
    macro_f1 = f1_score(y_true, y_pred, average="macro", zero_division=0)
    
    report = classification_report(y_true, y_pred, zero_division=0, output_dict=True)
    cm = confusion_matrix(y_true, y_pred, labels=["negative", "neutral", "positive"])
    
    metrics = {
        "dataset_version": "financial_phrasebank",
        "configuration": "sentences_75agree",
        "record_count": len(df),
        "accuracy": acc,
        "macro_f1": macro_f1,
        "classification_report": report,
        "confusion_matrix": {
            "labels": ["negative", "neutral", "positive"],
            "matrix": cm.tolist()
        }
    }
    
    with open(RESULTS_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
        
    logger.info(f"Evaluation complete. Accuracy: {acc:.4f}, Macro F1: {macro_f1:.4f}")
    
    # Identify some misclassifications
    misclassified = df[df["true_label"] != df["pred_label"]]
    misclassified.head(10).to_csv(RESULTS_DIR / "misclassifications_sample.csv", index=False)

if __name__ == "__main__":
    run_evaluation()
