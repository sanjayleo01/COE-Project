# API Documentation

The MVP includes an optional FastAPI adapter for integration testing and future deployment.

## GET /health
Returns a simple service health response.

## POST /analyze
Accepts the five evidence streams plus order/fit context and returns:
- predicted label
- confidence
- high-priority flag
- evidence count
- evidence bundle

Input validation is handled by Pydantic. Unexpected analysis failures are returned as a structured ANALYSIS_ERROR response.

## POST /workload/check
Accepts worker_id and requested_tasks and returns the safe assignment, overflow and safety state. The hard limit remains 25 tasks per worker.

Run with:
uvicorn structured_return_reason_analyser.src.api:app --reload

The Streamlit UI remains the primary human-facing interface.
