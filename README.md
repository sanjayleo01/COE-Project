# Structured Return-Reason Analyser — C28 CoE Growth Project

The repository contains the review-ready MVP under **structured_return_reason_analyser/**.

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

## Run
```bash
pip install -r requirements.txt
python generate_data.py
python evaluate.py
python -m pytest structured_return_reason_analyser/tests -q
streamlit run app.py
```

The detailed implementation lives in `structured_return_reason_analyser/src/`, with experiment, architecture, risk, stakeholder-validation and Phase 2 documentation in `structured_return_reason_analyser/docs/`.

The supplied evaluation dataset is synthetic and reproducible. Its metrics demonstrate end-to-end engineering behavior, not production accuracy. Production rollout requires an independently audited real-return holdout.

See `structured_return_reason_analyser/docs/PHASE_2_REPORT.md` for the Qbee review summary.
