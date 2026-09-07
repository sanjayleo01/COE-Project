"""
app.py
-------
A simple Streamlit dashboard so the analyser isn't just a terminal script --
this is what you'd show a "product team" stakeholder or a viva panel.

Run with:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
from analyser import analyse_dataset
from evaluate import attach_ground_truth, evaluate_predictions
from workload import assign_high_priority_returns, verify_no_worker_overloaded, MAX_INSPECTIONS_PER_WORKER_PER_DAY

st.set_page_config(page_title="Return Root-Cause Analyser", layout="wide")
st.title("Fashion Marketplace: Return Root-Cause Analyser")
st.caption("Turns vague return reasons into structured, evidence-backed, actionable labels.")

products_df = pd.read_csv("data/products.csv")
listings_df = pd.read_csv("data/listings.csv")
inspections_df = pd.read_csv("data/inspections.csv")

scenario = st.radio("Choose scenario to analyse:", ["Normal day", "Disruption day (missing data + spike)"], horizontal=True)
returns_path = "data/returns_normal_day.csv" if scenario == "Normal day" else "data/returns_disruption_day.csv"
returns_df = pd.read_csv(returns_path)

results_df = analyse_dataset(returns_df, products_df, listings_df, inspections_df)
results_df = attach_ground_truth(results_df, products_df)
metrics, false_positives, false_negatives = evaluate_predictions(results_df)

# ---------------- Top metrics ----------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total returns", metrics["total_returns"])
c2.metric("Exact label accuracy", f"{metrics['exact_label_accuracy']*100:.1f}%")
c3.metric("False positive rate", f"{metrics['false_positive_rate']*100:.1f}%")
c4.metric("False negative rate", f"{metrics['false_negative_rate']*100:.1f}%")

st.divider()

# ---------------- Before / After ----------------
st.subheader("Before vs After")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**BEFORE** (old signal: `customer_action` only)")
    st.bar_chart(returns_df["customer_action"].value_counts())
    st.caption("Tells the product team nothing about WHY the item was returned.")
with col2:
    st.markdown("**AFTER** (structured root-cause label)")
    st.bar_chart(results_df["predicted_label"].value_counts())
    st.caption("Specific, actionable causes a product team can actually fix.")

st.divider()

# ---------------- High priority + evidence ----------------
st.subheader("High-priority flagged returns (with evidence)")
high = results_df[results_df["priority"] == "HIGH"][
    ["return_id", "product_id", "return_text", "predicted_label", "confidence", "evidence"]
]
st.dataframe(high, use_container_width=True)

st.divider()

# ---------------- False positives / negatives ----------------
st.subheader("Error inspection")
tab1, tab2 = st.tabs(["False Positives", "False Negatives"])
with tab1:
    st.caption("Analyser flagged a product issue, but it was really just customer preference.")
    st.dataframe(false_positives[["return_id", "return_text", "predicted_label", "true_root_cause"]], use_container_width=True)
with tab2:
    st.caption("Analyser missed a real, planted product issue.")
    st.dataframe(false_negatives[["return_id", "return_text", "predicted_label", "true_root_cause"]], use_container_width=True)

st.divider()

# ---------------- Worker workload safety ----------------
st.subheader("Warehouse worker workload safety")
workers = ["worker_A", "worker_B", "worker_C"]
assigned, queued, load = assign_high_priority_returns(results_df, workers)
is_safe, violations = verify_no_worker_overloaded(load)

c1, c2, c3 = st.columns(3)
c1.metric("Assigned today", len(assigned))
c2.metric("Queued for tomorrow", len(queued))
c3.metric("Cap per worker/day", MAX_INSPECTIONS_PER_WORKER_PER_DAY)

st.write("Load per worker:", load)
if is_safe:
    st.success("Safety check passed: no worker exceeds the daily cap.")
else:
    st.error(f"Safety violation: {violations}")
st.caption("Extra high-priority returns are queued for the next day instead of overloading a worker -- "
           "efficiency is never gained by unsafe assignment.")
