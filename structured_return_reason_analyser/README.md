# Structured Return-Reason Analyser — Review-Ready MVP

This folder contains the upgraded C28 MVP. It addresses the reviewer feedback by adding a hybrid semantic + rules analyser, explicit baseline/target measurement, normal/disruption evaluation, evidence-backed priority gates, error analysis, edge-case tests, stakeholder validation, and a 25-task worker safety cap.

## Run
```bash
pip install -r requirements.txt
python -m src.generate_data
python -m src.evaluate
python -m pytest -q
streamlit run src/app.py
```

## Labels
SIZE_TOO_SMALL, SIZE_TOO_LARGE, SIZE_CHART_MISMATCH, LISTING_CONTENT_ERROR, PRODUCT_SPEC_ERROR, CUSTOMER_ORDER_SELECTION, QUALITY_DAMAGE, UNKNOWN_REVIEW.

## Priority gate
High priority requires confidence >= 0.78 and at least 2 independent evidence streams. UNKNOWN_REVIEW is never auto-prioritised.

## Important validation note
The included dataset is synthetic and reproducible. Metrics are engineering validation, not proof of production accuracy. Production rollout requires an anonymised, independently audited real-return holdout set.
