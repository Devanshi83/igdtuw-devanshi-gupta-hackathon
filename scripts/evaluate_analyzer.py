"""Evaluate the rule-based event analyzer on a small, labeled test set.

This is a deterministic rule-checking exercise, not a measure of
real-world financial-news accuracy.
"""

from collections import defaultdict

from src.nlp.analyzer import analyze_text


CASES = [
    # Geopolitical
    ("geo_01", "War disrupts trade between the two countries.", "Geopolitical"),
    ("geo_02", "New sanctions were announced against the region.", "Geopolitical"),
    ("geo_03", "An invasion escalated the regional conflict.", "Geopolitical"),
    ("geo_04", "The conflict threatens supply chains.", "Geopolitical"),

    # Macroeconomic
    ("macro_01", "Inflation increased more than expected.", "Macroeconomic"),
    ("macro_02", "The central bank changed its interest rate.", "Macroeconomic"),
    ("macro_03", "Economists warned of a recession.", "Macroeconomic"),
    ("macro_04", "GDP growth slowed this quarter.", "Macroeconomic"),

    # Credit Event
    ("credit_01", "The company reported a debt default.", "Credit Event"),
    ("credit_02", "The lender faces serious liquidity concerns.", "Credit Event"),
    ("credit_03", "The firm filed for bankruptcy.", "Credit Event"),
    ("credit_04", "The issuer received a credit downgrade.", "Credit Event"),

    # Merger/Acquisition
    ("ma_01", "The companies announced a merger.", "Merger/Acquisition"),
    ("ma_02", "The acquisition will close next quarter.", "Merger/Acquisition"),
    ("ma_03", "A rival proposed a takeover.", "Merger/Acquisition"),
    ("ma_04", "The board approved a buyout.", "Merger/Acquisition"),

    # Product/Cyber Event
    ("product_01", "The company announced a product launch.", "Product/Cyber Event"),
    ("product_02", "A cybersecurity incident disrupted operations.", "Product/Cyber Event"),
    ("product_03", "A product recall was announced.", "Product/Cyber Event"),
    ("product_04", "A service outage affected customers.", "Product/Cyber Event"),

    # Other
    ("other_01", "The company appointed a new chief executive.", "Other"),
    ("other_02", "The firm opened a new regional office.", "Other"),
    ("other_03", "The company published its annual report.", "Other"),
    ("other_04", "Management scheduled an investor meeting.", "Other"),

    # Boundary and priority checks
    ("edge_01", "The software team released an update.", "Other"),
    ("edge_02", "The product launch followed a successful merger.", "Merger/Acquisition"),
    ("edge_03", "The bank reported a default after the invasion.", "Geopolitical"),
    ("edge_04", "A product launch was delayed by a service outage.", "Product/Cyber Event"),
]


def main():
    category_counts = defaultdict(lambda: {"correct": 0, "total": 0})
    mismatches = []

    for case_id, text, expected in CASES:
        result = analyze_text(text)
        actual = result["event_classification"]

        category_counts[expected]["total"] += 1
        if actual == expected:
            category_counts[expected]["correct"] += 1
        else:
            mismatches.append(
                {
                    "id": case_id,
                    "expected": expected,
                    "actual": actual,
                    "text": text,
                }
            )

    correct = len(CASES) - len(mismatches)
    accuracy = correct / len(CASES) if CASES else 0.0

    print("SIGNAL-TO-SHOCK ANALYZER EVALUATION")
    print("=" * 42)
    print("Method: deterministic, hand-labeled rule-checking set")
    print(f"Cases: {len(CASES)}")
    print(f"Correct classifications: {correct}")
    print(f"Mismatches: {len(mismatches)}")
    print(f"Agreement with expected labels: {accuracy:.1%}")
    print("\nPER-CATEGORY RESULTS")

    for category in sorted(category_counts):
        stats = category_counts[category]
        rate = stats["correct"] / stats["total"]
        print(
            f"{category}: {stats['correct']}/{stats['total']} "
            f"({rate:.1%})"
        )

    print("\nMISMATCH DETAILS")
    if not mismatches:
        print("No mismatches on this test set.")
    else:
        for item in mismatches:
            print(f"\n{item['id']}: {item['text']}")
            print(f"  Expected: {item['expected']}")
            print(f"  Actual:   {item['actual']}")

    print(
        "\nCaution: these results measure agreement with this small, "
        "hand-authored test set. They do not establish real-world "
        "financial-news classification accuracy."
    )


if __name__ == "__main__":
    main()
