"""Compatibility entry point for the upgraded C28 MVP."""
from structured_return_reason_analyser.src.workload import enforce_workload,safe_batch_assign,WORKER_TASK_CAP
if __name__=="__main__":
    print({"worker_task_cap":WORKER_TASK_CAP,"example":enforce_workload("worker_A",30).__dict__})
