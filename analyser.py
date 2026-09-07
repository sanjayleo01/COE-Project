"""
analyser.py
------------
This is the HEART of the project: the "structured return-reason analyser".

WHAT IT DOES (in plain words):
For every return, it looks at 4 things:
  1. return_text          -> what the customer typed
  2. product attributes    -> e.g. is the size chart marked accurate?
  3. listing content        -> e.g. is the listing photo marked accurate?
  4. inspection findings    -> what the warehouse found when they checked it

It then scores each possible ROOT CAUSE LABEL based on simple, visible
keyword + attribute RULES (no black-box ML), and picks the best one.

WHY RULE-BASED?
Every score comes from clearly listed rules, so we can always show EVIDENCE
("this was flagged because the text contained the word 'small' AND the
size chart was marked inaccurate"). That is required by the project brief
("provide evidence for every high-priority output") and is much easier to
defend in a viva than a black-box ML model.

LABELS
------
SIZE_CHART_ERROR        - size chart is wrong for this product
PHOTO_MISLEADING        - listing photo doesn't match the real item
MATERIAL_MISMATCH       - fabric/material doesn't match what's listed
DESCRIPTION_INACCURATE  - listing text has wrong specs
QUALITY_DEFECT          - manufacturing defect / damage
CUSTOMER_PREFERENCE     - not a product problem (customer changed mind etc.)
UNKNOWN                 - not enough evidence to decide (needs manual review)

THRESHOLDS
----------
score >= 0.7        -> HIGH priority  (confident, actionable)
0.4 <= score < 0.7  -> MEDIUM priority (possible issue, needs review)
score < 0.4          -> LOW / UNKNOWN  (not enough signal)
"""

import pandas as pd

# Keywords that hint at each root cause, found in customer's return_text
KEYWORDS = {
    "SIZE_CHART_ERROR": ["size chart", "size guide", "runs small", "runs large",
                          "doesn't fit", "didn't fit", "too tight", "too small", "too big"],
    "PHOTO_MISLEADING": ["photo", "picture", "looks different", "different color",
                          "different length", "misleading"],
    "MATERIAL_MISMATCH": ["material", "fabric", "cheap", "not genuine", "quality does not match"],
    "DESCRIPTION_INACCURATE": ["description", "listing said", "specification", "specs"],
    "QUALITY_DEFECT": ["defect", "damaged", "torn", "tear", "stitching", "thread loose", "broken"],
    "CUSTOMER_PREFERENCE": ["changed my mind", "don't need", "mistake", "better price",
                             "didn't like the color", "no longer"],
}

HIGH_THRESHOLD = 0.7
MEDIUM_THRESHOLD = 0.4


def score_return(return_text, product_row, listing_row, inspection_notes):
    """
    Scores every label for ONE return.
    Returns a dict: {label: (score, [evidence_reasons])}
    """
    # handle missing text robustly: empty string, None, or pandas NaN (a float)
    # all mean "customer left no comment" -- common on disruption days
    if return_text is None or (isinstance(return_text, float)):
        return_text = ""
    text = str(return_text).lower()
    scores = {label: 0.0 for label in KEYWORDS}
    evidence = {label: [] for label in KEYWORDS}

    # ---- RULE 1: keyword match in customer's return text (worth 0.4) ----
    for label, words in KEYWORDS.items():
        for w in words:
            if w in text:
                scores[label] += 0.4
                evidence[label].append(f"return text contains '{w}'")
                break  # only count once per label from text

    # ---- RULE 2: product attribute cross-check (worth 0.3) ----
    if product_row is not None:
        if product_row.get("size_chart_accurate") is False:
            scores["SIZE_CHART_ERROR"] += 0.3
            evidence["SIZE_CHART_ERROR"].append("product's size_chart_accurate = False")

    # ---- RULE 3: listing content cross-check (worth 0.3) ----
    if listing_row is not None:
        if listing_row.get("photo_accurate") is False:
            scores["PHOTO_MISLEADING"] += 0.3
            evidence["PHOTO_MISLEADING"].append("listing's photo_accurate = False")

    # ---- RULE 4: inspection findings (worth 0.3, strongest real proof) ----
    notes = (inspection_notes or "").lower()
    inspection_map = {
        "SIZE_CHART_ERROR": "dimensions smaller than size chart",
        "PHOTO_MISLEADING": "color/pattern differs from listing photo",
        "MATERIAL_MISMATCH": "fabric composition does not match",
        "DESCRIPTION_INACCURATE": "listed specification not present",
        "QUALITY_DEFECT": "manufacturing defect",
    }
    # Inspection findings get MORE weight (0.5) than text/attributes/listing
    # (0.3-0.4 each). Why: physical inspection is objective proof a human
    # verified, while customer text is self-reported and can be vague or
    # even wrong about the real cause. Found during edge-case testing
    # (test_edge_cases.py, Edge Case 4) where a customer wrote "changed my
    # mind" but the item had a confirmed defect -- the analyser must trust
    # the inspection over the customer's words.
    for label, phrase in inspection_map.items():
        if phrase in notes:
            scores[label] += 0.5
            evidence[label].append(f"inspection notes confirm: '{phrase}'")

    # cap every score at 1.0
    for label in scores:
        scores[label] = min(scores[label], 1.0)

    return scores, evidence


def classify_return(return_text, product_row, listing_row, inspection_notes):
    """
    Runs scoring, then picks the single best label + priority tier.
    Returns a dict with everything needed for the report / dashboard.
    """
    scores, evidence = score_return(return_text, product_row, listing_row, inspection_notes)

    best_label = max(scores, key=scores.get)
    best_score = scores[best_label]

    # If nothing scored meaningfully, and text hints at preference -> CUSTOMER_PREFERENCE
    # else -> UNKNOWN (needs manual review, per project requirement)
    if best_score < MEDIUM_THRESHOLD:
        best_label = "UNKNOWN"
        priority = "LOW"
    elif best_score < HIGH_THRESHOLD:
        priority = "MEDIUM"
    else:
        priority = "HIGH"

    return {
        "predicted_label": best_label,
        "confidence": round(best_score, 2),
        "priority": priority,
        "evidence": evidence.get(best_label, []),
        "all_scores": {k: round(v, 2) for k, v in scores.items()},
    }


def analyse_dataset(returns_df, products_df, listings_df, inspections_df):
    """
    Runs classify_return() over an entire returns file and joins in
    product/listing/inspection context for each row.
    Returns a results DataFrame ready for evaluation / display.
    """
    products_idx = products_df.set_index("product_id").to_dict("index")
    listings_idx = listings_df.set_index("product_id").to_dict("index")

    # take the most recent / first inspection note found for each product
    insp_by_product = (
        inspections_df.groupby("product_id")["inspection_notes"].first().to_dict()
    )

    results = []
    for _, ret in returns_df.iterrows():
        pid = ret["product_id"]
        product_row = products_idx.get(pid)
        listing_row = listings_idx.get(pid)
        inspection_notes = insp_by_product.get(pid, "")

        result = classify_return(ret["return_text"], product_row, listing_row, inspection_notes)

        results.append({
            "return_id": ret["return_id"],
            "product_id": pid,
            "return_text": ret["return_text"],
            "customer_action": ret["customer_action"],
            "predicted_label": result["predicted_label"],
            "confidence": result["confidence"],
            "priority": result["priority"],
            "evidence": "; ".join(result["evidence"]) if result["evidence"] else "no strong signal",
        })

    return pd.DataFrame(results)


if __name__ == "__main__":
    products_df = pd.read_csv("data/products.csv")
    listings_df = pd.read_csv("data/listings.csv")
    inspections_df = pd.read_csv("data/inspections.csv")
    returns_df = pd.read_csv("data/returns_normal_day.csv")

    results_df = analyse_dataset(returns_df, products_df, listings_df, inspections_df)
    results_df.to_csv("data/analysed_normal_day.csv", index=False)
    print(results_df["predicted_label"].value_counts())
    print("\nSaved -> data/analysed_normal_day.csv")
