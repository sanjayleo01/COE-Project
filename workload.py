"""
workload.py
------------
WHY THIS FILE EXISTS:
The project brief asks for "worker/driver workload limits" and proof that
"efficiency is not gained through unsafe assignment." In OUR system, the
people this applies to are the WAREHOUSE STAFF who physically re-inspect
items that our analyser flags as HIGH priority (i.e. confident, likely
preventable issues worth a second look).

Without a limit, a naive "efficient" system would dump ALL high-priority
returns onto whichever worker is fastest -- which is unsafe / unsustainable
for that worker. This module enforces a hard per-worker daily cap and
proves that no worker ever exceeds it, even when there's a backlog.
"""

import pandas as pd

MAX_INSPECTIONS_PER_WORKER_PER_DAY = 25  # safety limit, adjustable


def assign_high_priority_returns(results_df, workers):
    """
    Takes only HIGH priority returns (the ones worth a human inspector's time)
    and distributes them round-robin across workers, WITHOUT ever exceeding
    MAX_INSPECTIONS_PER_WORKER_PER_DAY.

    If there are more HIGH priority items than total safe capacity, the
    extras are queued for the NEXT day instead of overloading anyone.
    This is the "efficiency must not come from unsafe assignment" proof.
    """
    high_priority = results_df[results_df["priority"] == "HIGH"].copy()

    total_capacity = len(workers) * MAX_INSPECTIONS_PER_WORKER_PER_DAY
    assigned_today = high_priority.iloc[:total_capacity].copy()
    queued_for_next_day = high_priority.iloc[total_capacity:].copy()

    # round-robin assignment, capped per worker
    worker_load = {w: 0 for w in workers}
    assignments = []
    worker_cycle = list(workers)
    idx = 0
    for _, row in assigned_today.iterrows():
        # find next worker who still has capacity
        tries = 0
        while worker_load[worker_cycle[idx % len(worker_cycle)]] >= MAX_INSPECTIONS_PER_WORKER_PER_DAY:
            idx += 1
            tries += 1
            if tries > len(worker_cycle):
                break  # nobody has capacity (shouldn't happen given total_capacity check)
        w = worker_cycle[idx % len(worker_cycle)]
        worker_load[w] += 1
        assignments.append(w)
        idx += 1

    assigned_today["assigned_worker"] = assignments
    return assigned_today, queued_for_next_day, worker_load


def verify_no_worker_overloaded(worker_load):
    """Simple safety check used as PROOF in the report / viva."""
    violations = {w: n for w, n in worker_load.items() if n > MAX_INSPECTIONS_PER_WORKER_PER_DAY}
    return len(violations) == 0, violations


if __name__ == "__main__":
    results_df = pd.read_csv("data/evaluated_normal_day.csv")
    workers = ["worker_A", "worker_B", "worker_C"]

    assigned, queued, load = assign_high_priority_returns(results_df, workers)

    print(f"Total HIGH priority returns today: {len(results_df[results_df['priority'] == 'HIGH'])}")
    print(f"Assigned today: {len(assigned)}   Queued for next day: {len(queued)}")
    print("\nWorker load (max allowed =", MAX_INSPECTIONS_PER_WORKER_PER_DAY, "):")
    for w, n in load.items():
        print(f"  {w}: {n} inspections")

    is_safe, violations = verify_no_worker_overloaded(load)
    print(f"\nSafety check passed: {is_safe}")
    if not is_safe:
        print("VIOLATIONS:", violations)

    assigned.to_csv("data/worker_assignments.csv", index=False)
