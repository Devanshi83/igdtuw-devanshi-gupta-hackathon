"""Evaluate sentiment and impact behavior on hand-authored examples."""

from src.nlp.analyzer import analyze_text, SEVERITY


CASES = [
    {
        "id": "positive",
        "text": "Strong profit growth and record gains.",
        "sentiment": "positive",
    },
    {
        "id": "negative",
        "text": "The company reported fraud, losses and a crisis.",
        "sentiment": "negative",
    },
    {
        "id": "neutral",
        "text": "The company held its annual meeting.",
        "sentiment": "neutral",
    },
    {
        "id": "mixed",
        "text": "Profit growth continued despite a major loss.",
        "sentiment": "mixed",
    },
    {
        "id": "three_negative_terms",
        "text": "A credit default caused a crisis and liquidity risk.",
        "sentiment": "negative",
    },
    {
        "id": "geopolitical_severity",
        "text": "War disrupted trade.",
        "sentiment": "neutral",
    },
    {
        "id": "macroeconomic_severity",
        "text": "Inflation increased.",
        "sentiment": "neutral",
    },
    {
        "id": "other_severity",
        "text": "The company held an annual meeting.",
        "sentiment": "neutral",
    },
]


def expected_sentiment(label):
    return {
        "positive": lambda score: score > 0,
        "negative": lambda score: score < 0,
        "neutral": lambda score: score == 0,
        "mixed": lambda score: -1 < score < 1 and score != 0,
    }[label]


def main():
    sentiment_pass = 0
    impact_pass = 0

    print("SENTIMENT AND IMPACT EVALUATION")
    print("=" * 40)

    for case in CASES:
        result = analyze_text(case["text"])
        score = result["sentiment_score"]
        sentiment_ok = expected_sentiment(case["sentiment"])(score)

        category = result["event_classification"]
        expected_base = SEVERITY[category]
        negative_count = result["evidence"]["negative_keyword_count"]
        expected_impact = (
            min(10, expected_base + 1) if negative_count >= 3
            else expected_base
        )
        impact_ok = result["impact_score"] == expected_impact
        impact_range_ok = 1 <= result["impact_score"] <= 10

        sentiment_pass += int(sentiment_ok)
        impact_pass += int(impact_ok and impact_range_ok)

        print(f"\nCase: {case['id']}")
        print(f"  Sentiment: {score} | Expected pattern: {case['sentiment']} "
              f"| {'PASS' if sentiment_ok else 'FAIL'}")
        print(f"  Category: {category}")
        print(f"  Negative keyword count: {negative_count}")
        print(f"  Impact: {result['impact_score']} "
              f"| Rule-expected: {expected_impact} "
              f"| {'PASS' if impact_ok and impact_range_ok else 'FAIL'}")

    print("\nSUMMARY")
    print(f"Sentiment pattern checks: {sentiment_pass}/{len(CASES)}")
    print(f"Impact rule checks: {impact_pass}/{len(CASES)}")
    print(
        "\nNote: these checks verify consistency with simple, "
        "hand-authored expectations and the implemented rules. "
        "They do not validate sentiment quality or real-world impact."
    )


if __name__ == "__main__":
    main()
