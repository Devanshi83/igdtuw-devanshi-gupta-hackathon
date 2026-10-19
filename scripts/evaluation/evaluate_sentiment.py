"""Evaluate frozen sentiment rules. Never tune on these evaluation labels."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.nlp.analyzer import analyze_text
RESULTS_DIR = ROOT / 'results/real_data'
LABELS = ['negative', 'neutral', 'positive']


def map_score_to_label(score):
    return 'positive' if score > 0 else 'negative' if score < 0 else 'neutral'


def run_evaluation(input_csv=None):
    if input_csv:
        df = pd.read_csv(input_csv)
        if not {'text', 'true_label'}.issubset(df.columns):
            raise ValueError('CSV requires text and true_label columns')
        df = df[['text', 'true_label']].copy()
    else:
        from datasets import load_dataset
        dataset = load_dataset('financial_phrasebank', 'sentences_75agree', split='train', trust_remote_code=True)
        df = pd.DataFrame([{'text':r['sentence'], 'true_label':LABELS[r['label']]} for r in dataset])
    if df.empty or df.text.isna().any() or not df.true_label.isin(LABELS).all():
        raise ValueError('Non-empty text and valid sentiment labels are required')
    signals = [analyze_text(t) for t in df.text]
    df['sentiment_score'] = [s['sentiment_score'] for s in signals]
    df['pred_label'] = df.sentiment_score.map(map_score_to_label)
    df['event_classification'] = [s['event_classification'] for s in signals]
    y_true, y_pred = df.true_label, df.pred_label
    majority_label = y_true.value_counts().idxmax()
    majority_predictions = [majority_label] * len(df)
    metrics = {
        'dataset_version':'financial_phrasebank', 'configuration':'sentences_75agree',
        'record_count':len(df), 'accuracy':accuracy_score(y_true, y_pred),
        'macro_f1':f1_score(y_true, y_pred, average='macro', zero_division=0),
        'classification_report':classification_report(y_true, y_pred, output_dict=True, zero_division=0),
        'confusion_matrix':{'labels':LABELS, 'matrix':confusion_matrix(y_true, y_pred, labels=LABELS).tolist()},
        'majority_baseline':{'label':majority_label, 'accuracy':accuracy_score(y_true, majority_predictions),
                             'macro_f1':f1_score(y_true, majority_predictions, average='macro', zero_division=0)},
        'provenance':{'evaluation_date':'2026-10-19', 'model_version':signals[0]['model_version'],
                      'analyzer_sha256':hashlib.sha256((ROOT/'src/nlp/analyzer.py').read_bytes()).hexdigest(),
                      'input_sha256':hashlib.sha256(df[['text','true_label']].to_csv(index=False).encode()).hexdigest(),
                      'source':'Local retained Financial PhraseBank labelled evaluation input' if input_csv else 'Hugging Face Financial PhraseBank',
                      'scope':'Sentiment only. No training or label-driven tuning.'},
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    (RESULTS_DIR/'metrics.json').write_text(json.dumps(metrics, indent=2)+'\n')
    df.to_csv(RESULTS_DIR/'predictions.csv', index=False)
    df.loc[y_true != y_pred].head(10).to_csv(RESULTS_DIR/'misclassifications_sample.csv', index=False)
    print(json.dumps({k:metrics[k] for k in ['record_count','accuracy','macro_f1','majority_baseline']}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-csv', type=Path, help='Locally held labelled CSV (text,true_label); do not commit licensed text')
    run_evaluation(parser.parse_args().input_csv)
