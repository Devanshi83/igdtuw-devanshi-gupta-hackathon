EVENT_RULES = {
    "Geopolitical": ["war", "sanction", "invasion", "conflict"],
    "Macroeconomic": ["inflation", "interest rate", "recession", "gdp"],
    "Credit Event": ["default", "liquidity", "bankruptcy", "downgrade"],
    "Merger/Acquisition": ["merger", "acquisition", "takeover", "buyout"],
    "Product/Cyber Event": [
        "cybersecurity", "breach", "product launch", "recall", "outage"
    ],
}

SEVERITY = {
    "Geopolitical": 9,
    "Macroeconomic": 7,
    "Credit Event": 9,
    "Merger/Acquisition": 5,
    "Product/Cyber Event": 6,
    "Other": 3,
}

POSITIVE = {
    "growth", "profit", "surge", "upgrade", "recovery",
    "strong", "record", "gain", "beat"
}

NEGATIVE = {
    "loss", "default", "crisis", "breach", "fraud", "decline",
    "fall", "drop", "downgrade", "recession", "bankruptcy",
    "liquidity", "disruption", "risk", "warning"
}


def analyze_text(text):
    """Explainable keyword baseline; not a trained NLP model."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    normalized = text.lower()
    words = normalized.replace(",", " ").replace(".", " ").split()

    positive = sum(word.strip("!?;:") in POSITIVE for word in words)
    negative = sum(word.strip("!?;:") in NEGATIVE for word in words)

    total = positive + negative
    sentiment = (positive - negative) / total if total else 0.0

    event = "Other"
    for category, keywords in EVENT_RULES.items():
        if any(keyword in normalized for keyword in keywords):
            event = category
            break

    impact = SEVERITY[event]
    if negative >= 3:
        impact = min(10, impact + 1)

    return {
        "sentiment_score": round(sentiment, 3),
        "event_classification": event,
        "impact_score": impact,
        "method": "keyword baseline",
        "evidence": {
            "positive_keyword_count": positive,
            "negative_keyword_count": negative,
            "matched_category": event,
        },
    }
