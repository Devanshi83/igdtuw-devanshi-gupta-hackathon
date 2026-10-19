import re

EVENT_RULES = {
    "Geopolitical": ["war", r"sanctions?", "invasion", "conflict"],
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

    normalized = text.casefold()
    words = re.findall(r"\b[\w']+\b", normalized)

    positive = sum(word in POSITIVE for word in words)
    negative = sum(word in NEGATIVE for word in words)

    total = positive + negative
    sentiment = (positive - negative) / total if total else 0.0

    event = "Other"
    for category, keywords in EVENT_RULES.items():
        if any(
            re.search(rf"\b{keyword.casefold()}\b", normalized)
            for keyword in keywords
        ):
            event = category
            break

    category_matches = {
        category: sorted({match.group(0) for keyword in keywords
                          for match in re.finditer(rf"\b{keyword.casefold()}\b", normalized)})
        for category, keywords in EVENT_RULES.items()
    }
    category_matches = {key: value for key, value in category_matches.items() if value}
    review_reasons = []
    if not text.strip():
        review_reasons.append("Empty input")
    if not category_matches:
        review_reasons.append("No supported event keywords")
    if len(category_matches) > 1:
        review_reasons.append("Multiple event categories matched; choose a scenario explicitly")
    if re.search(r"\b(no|not|never|denies|denied|without|unlikely)\b", normalized):
        review_reasons.append("Possible negation; keyword rules cannot resolve context")

    impact = SEVERITY[event]
    if negative >= 3:
        impact = min(10, impact + 1)

    return {
        "sentiment_score": round(sentiment, 3),
        "event_classification": event,
        "impact_score": impact,
        "method": "keyword baseline",
        "model_version": "keyword-v1-evidence-v2",
        "review_required": bool(review_reasons),
        "review_reasons": review_reasons,
        "evidence": {
            "positive_keyword_count": positive,
            "negative_keyword_count": negative,
            "matched_category": event,
            "category_matches": category_matches,
            "positive_keywords": sorted(set(words) & POSITIVE),
            "negative_keywords": sorted(set(words) & NEGATIVE),
            "selection_policy": "First matching category in configured order; review ambiguity",
            "sentiment_formula": "(positive_count - negative_count) / total_keyword_count",
        },
    }
