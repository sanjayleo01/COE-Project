from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .analyser import ReturnReasonAnalyser
from .workload import enforce_workload
from .storage import init_db
from .errors import safe_error

app = FastAPI(title="Structured Return-Reason Analyser API", version="1.0")
model = ReturnReasonAnalyser()

class ReturnRequest(BaseModel):
    return_text: str = ""
    product_attribute: str = ""
    size_chart: str = ""
    fit_type: str = ""
    listing_content: str = ""
    customer_action: str = ""
    inspection_finding: str = ""
    ordered_size: str = ""

class WorkloadRequest(BaseModel):
    worker_id: str = Field(min_length=1, max_length=64)
    requested_tasks: int = Field(ge=0, le=10000)

@app.get("/health")
def health():
    return {"status": "ok", "service": "return-reason-analyser"}

@app.post("/analyze")
def analyze(req: ReturnRequest):
    try:
        return {"ok": True, "result": model.predict(req.model_dump())}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=safe_error(str(exc), "ANALYSIS_ERROR"))

@app.post("/workload/check")
def workload_check(req: WorkloadRequest):
    try:
        assignment = enforce_workload(req.worker_id, req.requested_tasks)
        return {"ok": True, "assignment": assignment.__dict__}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=safe_error(str(exc), "WORKLOAD_ERROR"))

@app.on_event("startup")
def startup():
    init_db()
