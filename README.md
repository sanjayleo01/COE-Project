# Structured Return-Reason Analyser — C28 CoE Growth Project

The repository contains the review-ready MVP under structured_return_reason_analyser/.

## Phase 3 improvements
- Hybrid rules + TF-IDF semantic analysis
- Baseline vs improved experiment
- Five evidence streams
- Explicit confidence/evidence gate
- False-positive/false-negative artifact
- Normal and disruption testing
- Edge/failure and regression tests
- Worker safety cap of 25 tasks/shift
- Stakeholder validation workflow
- Streamlit dashboard
- Optional FastAPI integration layer
- SQLite persistence with documented schema
- Structured API error boundaries
- GitHub Actions CI running the test suite
- .gitignore for caches and local database files

## Run
pip install -r requirements.txt
python generate_data.py
python evaluate.py
python -m pytest structured_return_reason_analyser/tests -q
streamlit run app.py

## Optional API
uvicorn structured_return_reason_analyser.src.api:app --reload

Endpoints: GET /health, POST /analyze, POST /workload/check.
API details: structured_return_reason_analyser/docs/API.md

## Database
SQLite persistence is documented in structured_return_reason_analyser/docs/DATABASE_SCHEMA.md and executable SQL is in structured_return_reason_analyser/sql/schema.sql.

## Testing and error boundaries
Unit, integration, workload, persistence and error-boundary tests are in structured_return_reason_analyser/tests/.
CI configuration: .github/workflows/test.yml

## Evidence and safety
High-priority output requires confidence >= 0.78 plus at least 2 independent evidence streams. Worker assignment has a hard 25-task cap and overflow remains unassigned.

## Data limitation
The evaluation data is synthetic and reproducible. Reported metrics demonstrate system behavior, not production generalisation. Production rollout requires an independently audited real-return holdout.

See structured_return_reason_analyser/docs/PHASE_2_REPORT.md, TESTING_AND_ERROR_BOUNDARIES.md and RISK_REGISTER.md.