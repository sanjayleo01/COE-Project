from structured_return_reason_analyser.src.api import health, analyze, workload_check, ReturnRequest, WorkloadRequest

def test_health_contract():
    assert health()["status"] == "ok"

def test_analyze_contract():
    request = ReturnRequest(
        return_text="too tight",
        product_attribute="chest 40",
        size_chart="chest 40",
        listing_content="fits true to size",
        customer_action="customer tried on",
        inspection_finding="no damage",
    )
    response = analyze(request)
    assert response["ok"] is True
    assert "predicted_label" in response["result"]
    assert "confidence" in response["result"]
    assert "evidence" in response["result"]

def test_workload_contract():
    response = workload_check(WorkloadRequest(worker_id="w1", requested_tasks=30))
    assert response["ok"] is True
    assert response["assignment"]["assigned"] == 25
    assert response["assignment"]["overflow"] == 5
    assert response["assignment"]["safe"] is False
