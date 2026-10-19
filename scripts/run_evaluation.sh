#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

export PYTHONPATH=.

echo "===== AUTOMATED TESTS ====="
python -m pytest -q

echo
echo "===== EVENT CLASSIFICATION ====="
python scripts/evaluate_analyzer.py

echo
echo "===== SENTIMENT AND IMPACT ====="
python scripts/evaluate_sentiment_impact.py

echo
echo "===== PORTFOLIO STRESS ====="
python scripts/evaluate_portfolio.py

echo
echo "All evaluation commands completed successfully."
