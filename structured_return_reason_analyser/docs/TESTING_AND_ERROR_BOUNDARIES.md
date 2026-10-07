# Testing and Error Boundaries

## Unit testing
The suite covers normal prediction, missing text, contradictory evidence, missing fields, empty evidence fallback, damage precedence, workload limits, batch allocation and SQLite persistence.

## Error boundaries
1. API validation rejects malformed requests through Pydantic.
2. Analysis failures are converted to a structured ANALYSIS_ERROR response.
3. Workload requests are bounded and never exceed the 25-task safety cap.
4. SQLite initialisation creates required tables before writes.
5. Streamlit stops with a user-readable setup message when evaluation data is unavailable.

## Regression
Every change should run:
python -m pytest -q

GitHub Actions runs the same test suite on push and pull request.
