CREATE TABLE returns (
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

CREATE TABLE predictions (
    prediction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_id TEXT NOT NULL REFERENCES returns(return_id),
    predicted_label TEXT NOT NULL,
    confidence REAL NOT NULL,
    high_priority INTEGER NOT NULL,
    evidence_count INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE evidence (
    evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_id TEXT NOT NULL REFERENCES returns(return_id),
    prediction_id INTEGER REFERENCES predictions(prediction_id),
    source TEXT NOT NULL,
    evidence_text TEXT NOT NULL
);

CREATE TABLE stakeholder_validation (
    validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    return_id TEXT,
    product_id TEXT,
    root_cause TEXT NOT NULL,
    decision TEXT NOT NULL,
    action TEXT,
    reviewer TEXT,
    validated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
