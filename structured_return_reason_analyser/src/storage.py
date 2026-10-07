import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS returns (
    return_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    ordered_size TEXT,
    return_text TEXT,
    product_attribute TEXT,
    size_chart TEXT,
    listing_content TEXT,
    customer_action TEXT,
    inspection_finding TEXT,
    day_type TEXT
);
CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_id TEXT NOT NULL,
    predicted_label TEXT NOT NULL,
    confidence REAL NOT NULL,
    high_priority INTEGER NOT NULL,
    evidence_count INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(return_id) REFERENCES returns(return_id)
);
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_id TEXT NOT NULL,
    prediction_id INTEGER,
    source TEXT NOT NULL,
    evidence_text TEXT NOT NULL,
    FOREIGN KEY(return_id) REFERENCES returns(return_id),
    FOREIGN KEY(prediction_id) REFERENCES predictions(prediction_id)
);
CREATE TABLE IF NOT EXISTS stakeholder_validation (
    validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_id TEXT,
    product_id TEXT,
    root_cause TEXT NOT NULL,
    decision TEXT NOT NULL,
    action TEXT,
    reviewer TEXT,
    validated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

def init_db(db_path="data/returns.db"):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as conn:
        conn.executescript(SCHEMA)
    return str(path)

def save_return(db_path, row):
    init_db(db_path)
    fields = (
        "return_id", "product_id", "ordered_size", "return_text",
        "product_attribute", "size_chart", "listing_content",
        "customer_action", "inspection_finding", "day_type"
    )
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT OR REPLACE INTO returns VALUES (?,?,?,?,?,?,?,?,?,?)",
            tuple(row.get(field) for field in fields)
        )
