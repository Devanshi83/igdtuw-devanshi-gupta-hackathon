import json
from pathlib import Path

import pandas as pd
import pytest

# Adjust path to import map_score_to_label
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from scripts.evaluation.evaluate_sentiment import map_score_to_label

def test_map_score_to_label():
    assert map_score_to_label(0.5) == "positive"
    assert map_score_to_label(1.0) == "positive"
    assert map_score_to_label(-0.1) == "negative"
    assert map_score_to_label(-1.0) == "negative"
    assert map_score_to_label(0.0) == "neutral"

