# Database Schema

The MVP now includes a SQLite persistence layer.

Tables:
- returns: original return record and five evidence streams
- predictions: analyser label, confidence, priority and evidence count
- evidence: source-level evidence supporting a prediction
- stakeholder_validation: product-team review decision and action

Relationships:
returns.return_id -> predictions.return_id
returns.return_id -> evidence.return_id
predictions.prediction_id -> evidence.prediction_id

The executable schema is stored in sql/schema.sql. SQLite is used so evaluation does not require a production database server.
