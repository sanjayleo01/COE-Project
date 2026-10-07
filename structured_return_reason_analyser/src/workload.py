from dataclasses import dataclass
from .config import WORKER_TASK_CAP
@dataclass
class Assignment:
    worker_id:str
    assigned:int
    overflow:int
    safe:bool
def enforce_workload(worker_id,requested_tasks,cap=WORKER_TASK_CAP):
    requested_tasks=max(0,int(requested_tasks)); assigned=min(requested_tasks,cap)
    return Assignment(worker_id,assigned,requested_tasks-assigned,requested_tasks<=cap)
def safe_batch_assign(worker_ids,tasks):
    allocations={w:0 for w in worker_ids}; unassigned=0
    for _ in range(int(tasks)):
        candidates=[w for w in worker_ids if allocations[w]<WORKER_TASK_CAP]
        if not candidates: unassigned+=1; continue
        w=min(candidates,key=lambda x:allocations[x]); allocations[w]+=1
    return allocations,unassigned
