# Structured Return-Reason Analyser — C28 CoE Growth Project

This repository now contains the review-ready MVP under **structured_return_reason_analyser/**.

## Phase 2 improvements
- Hybrid rules + TF-IDF semantic analysis
- Baseline vs improved experiment
- Five evidence streams: return text, product attributes, listing content, customer action, inspection findings
- Confidence and high-priority thresholds
- Evidence bundle for every high-priority output
- False-positive / false-negative analysis
- Normal-day and disruption-day testing
- Edge/failure tests
- 25-task hard worker safety cap
- Stakeholder validation workflow
- Streamlit dashboard
- Reproducible synthetic dataset

## Run the upgraded MVP
```bash
pip install -r requirements.txt
python -m src.generate_data
python -m src.evaluate
python -m pytest -q
streamlit run src/app.py
```

For the upgraded package, use:
```text
structured_return_reason_analyser/
```

The supplied dataset is synthetic and reproducible. Metrics are engineering validation, not production accuracy. Production rollout requires an independently audited real-return holdout.

See `structured_return_reason_analyser/docs/PHASE_2_REPORT.md` for the Qbee review summary.
