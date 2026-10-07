class InvalidReturnRecord(ValueError):
    """Raised when return evidence cannot be normalised safely."""

class WorkloadSafetyError(ValueError):
    """Raised when a workload request cannot be safely interpreted."""

def safe_error(message, code):
    return {"error": {"code": code, "message": message}}
