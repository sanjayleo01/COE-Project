import sqlite3
from src.analyser import ReturnReasonAnalyser
from src.workload import enforce_workload, safe_batch_assign
from src.storage import init_db, save_return

def test_malformed_types_do_not_crash():
    out = ReturnReasonAnalyser().predict({
        "return_text": None,
        "size_chart": None,
        "product_attribute": None
    })
    assert "predicted_label" in out

def test_empty_evidence_is_conservative():
    out = ReturnReasonAnalyser().predict({
        "return_text": "",
        "product_attribute": "",
        "size_chart": "",
        "listing_content": "",
        "customer_action": "",
        "inspection_finding": ""
    })
    assert out["predicted_label"] == "UNKNOWN_REVIEW"
    assert not out["high_priority"]

def test_worker_negative_is_normalised():
    result = enforce_workload("worker-1", -4)
    assert result.assigned == 0
    assert result.overflow == 0

def test_empty_worker_pool_never_allocates():
    allocations, unassigned = safe_batch_assign([], 10)
    assert allocations == {}
    assert unassigned == 10

def test_sqlite_schema_and_write(tmp_path):
    db = str(tmp_path / "returns.db")
    init_db(db)
    save_return(db, {"return_id": "R1", "product_id": "P1", "ordered_size": "M"})
    with sqlite3.connect(db) as conn:
        row = conn.execute(
            "select return_id, product_id from returns where return_id='R1'"
        ).fetchone()
    assert row == ("R1", "P1")
