"""
generate_data.py
-----------------
Creates synthetic (fake but realistic) data for the fashion marketplace.

Why synthetic? Real return data isn't available for a college project, so we
BUILD the data ourselves and secretly "plant" the true root cause for each
product. This lets us later check: did our analyser find the same root cause
we planted? That's how we measure accuracy / false positives / negatives.

Produces 4 CSV files inside data/ :
  products.csv     -> product catalog + a hidden ground-truth issue
  listings.csv      -> the listing text customers actually see
  inspections.csv   -> warehouse notes after a returned item is inspected
  returns.csv        -> the actual return events with customer's free-text
"""

import pandas as pd
import random

random.seed(42)  # fixed seed so results are reproducible every run

# ---------------------------------------------------------------------
# STEP 1: Define a small set of products, each with a PLANTED ground
# truth issue. In real life we would never know this — here we set it
# ourselves so we can grade our own analyser later.
# ---------------------------------------------------------------------

PRODUCTS = [
    # product_id, category, true_root_cause, size_chart_correct, material
    ("P001", "T-Shirt",  "SIZE_CHART_ERROR",     False, "Cotton"),
    ("P002", "T-Shirt",  "NONE",                 True,  "Cotton"),
    ("P003", "Jeans",    "SIZE_CHART_ERROR",     False, "Denim"),
    ("P004", "Jeans",    "NONE",                 True,  "Denim"),
    ("P005", "Dress",    "PHOTO_MISLEADING",     True,  "Polyester"),
    ("P006", "Dress",    "NONE",                 True,  "Polyester"),
    ("P007", "Jacket",   "MATERIAL_MISMATCH",    True,  "Synthetic Leather"),
    ("P008", "Jacket",   "NONE",                 True,  "Genuine Leather"),
    ("P009", "Shoes",    "DESCRIPTION_INACCURATE", True, "Rubber"),
    ("P010", "Shoes",    "NONE",                 True,  "Rubber"),
    ("P011", "Saree",    "QUALITY_DEFECT",       True,  "Silk"),
    ("P012", "Saree",    "NONE",                 True,  "Silk"),
]

# Return-text phrase banks. Each root cause has typical customer phrasing.
# In a real system these would be learned from historical text; here we
# write them by hand for the simulation.
PHRASES = {
    "SIZE_CHART_ERROR": [
        "ordered M as per size chart but it fits like S",
        "size chart is wrong, way too tight",
        "followed the size guide and it still didn't fit",
        "runs very small compared to chart shown",
    ],
    "PHOTO_MISLEADING": [
        "looks completely different from the photo",
        "color and fit shown in picture is misleading",
        "photo showed a different length than what i received",
    ],
    "MATERIAL_MISMATCH": [
        "material feels cheap, not like the listing said",
        "fabric is not genuine leather as advertised",
        "material quality does not match description",
    ],
    "DESCRIPTION_INACCURATE": [
        "product description does not match what i received",
        "listing said memory foam sole but its hard rubber",
        "specifications in listing are incorrect",
    ],
    "QUALITY_DEFECT": [
        "thread coming loose, poor stitching",
        "defective piece, has a tear near the seam",
        "damaged item, stitching quality is bad",
    ],
    "NONE": [
        "changed my mind, don't need it anymore",
        "didn't like the color in person",
        "found a better price elsewhere",
        "ordered by mistake",
    ],
}

INSPECTION_NOTES = {
    "SIZE_CHART_ERROR": "Measured garment: dimensions smaller than size chart states.",
    "PHOTO_MISLEADING": "Physical item color/pattern differs from listing photo.",
    "MATERIAL_MISMATCH": "Fabric composition does not match listed material.",
    "DESCRIPTION_INACCURATE": "Listed specification not present on physical item.",
    "QUALITY_DEFECT": "Visible manufacturing defect / damage found.",
    "NONE": "No defect found. Item matches listing and size chart.",
}

CUSTOMER_ACTIONS = ["refund", "exchange", "store_credit"]


def build_products_and_listings():
    products_rows, listings_rows = [], []
    for pid, category, root_cause, size_chart_ok, material in PRODUCTS:
        products_rows.append({
            "product_id": pid,
            "category": category,
            "material": material,
            "size_chart_accurate": size_chart_ok,   # attribute used by analyser
            "true_root_cause": root_cause,           # HIDDEN ground truth (for grading only)
        })
        listings_rows.append({
            "product_id": pid,
            "listing_description": f"{category} made of {material}. True to size.",
            "photo_accurate": False if root_cause == "PHOTO_MISLEADING" else True,
        })
    return pd.DataFrame(products_rows), pd.DataFrame(listings_rows)


def build_inspections(products_df, n_per_product=3):
    rows = []
    insp_id = 1
    for _, prod in products_df.iterrows():
        for _ in range(n_per_product):
            rows.append({
                "inspection_id": f"I{insp_id:04d}",
                "product_id": prod["product_id"],
                "inspection_notes": INSPECTION_NOTES[prod["true_root_cause"]],
                "defect_found": prod["true_root_cause"] != "NONE",
            })
            insp_id += 1
    return pd.DataFrame(rows)


def build_returns(products_df, n_returns=200, disruption=False):
    """
    disruption=True simulates a 'bad day': missing text, missing inspection
    match, and a sudden spike of returns for ONE product (like a viral video
    causing a rush of returns). This is used later for the disruption test.
    """
    rows = []
    products = products_df.to_dict("records")

    for i in range(1, n_returns + 1):
        prod = random.choice(products)
        root_cause = prod["true_root_cause"]
        text = random.choice(PHRASES[root_cause])

        # simulate messy/missing data on disruption days
        if disruption and random.random() < 0.25:
            text = ""  # customer left no comment

        rows.append({
            "return_id": f"R{i:04d}",
            "product_id": prod["product_id"],
            "return_text": text,
            "customer_action": random.choice(CUSTOMER_ACTIONS),
        })

    if disruption:
        # spike: flood 40 extra returns for a single product (P001) in one day
        spike_prod = products_df.iloc[0]
        for j in range(40):
            rows.append({
                "return_id": f"RS{j:03d}",
                "product_id": spike_prod["product_id"],
                "return_text": random.choice(PHRASES[spike_prod["true_root_cause"]]),
                "customer_action": "refund",
            })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    products_df, listings_df = build_products_and_listings()
    inspections_df = build_inspections(products_df)

    normal_returns_df = build_returns(products_df, n_returns=200, disruption=False)
    disruption_returns_df = build_returns(products_df, n_returns=200, disruption=True)

    products_df.to_csv("data/products.csv", index=False)
    listings_df.to_csv("data/listings.csv", index=False)
    inspections_df.to_csv("data/inspections.csv", index=False)
    normal_returns_df.to_csv("data/returns_normal_day.csv", index=False)
    disruption_returns_df.to_csv("data/returns_disruption_day.csv", index=False)

    print("Data generated in data/ folder:")
    print(" - products.csv:", len(products_df), "rows")
    print(" - listings.csv:", len(listings_df), "rows")
    print(" - inspections.csv:", len(inspections_df), "rows")
    print(" - returns_normal_day.csv:", len(normal_returns_df), "rows")
    print(" - returns_disruption_day.csv:", len(disruption_returns_df), "rows")
