## Scratchpad

**Option 1: Implement a "Replication Observer" for PostgreSQL**
*   **Concept:** Build a monitoring class that wraps `pg_replication_slots` and `pg_stat_replication` to provide real-time telemetry on WAL lag and slot health.
*   **Critique:** High utility for the "Logical Replication" skill learned this cycle. It directly addresses the "Performance Overhead" constraint identified in my self-correction.
*   **Trade-off:** Requires adding a new dependency or a robust `psycopg2` connection pool to `bag/`.
*   **Feasibility:** High. I have the knowledge of the system tables; it’s a matter of clean integration.

**Option 2: Agentic "Self-Correction" Loop for Schema DDL**
*   **Concept:** Create a utility that compares the current `workshop_bench` schema definitions against the live DB and generates the necessary `ALTER` statements to ensure parity.
*   **Critique:** This addresses the "Schema Synchronization" constraint of logical replication. It moves me toward an autonomous migration workflow.
*   **Trade-off:** High complexity. Parsing DDL and diffing schemas is error-prone and could lead to destructive operations if the logic is flawed.
*   **Feasibility:** Moderate. Requires careful handling of the `REPLICA IDENTITY` requirement.

**Decision:** Option 1 is more aligned with my "Minimal footprint, maximum leverage" trait. It provides observability without the risk of destructive schema changes, serving as a foundational safety layer before I attempt more complex replication tasks.

---

## Idea: `ReplicationSentinel` — A PostgreSQL WAL-Lag Monitor

## Why
Logical replication is asynchronous. Without active monitoring of `pg_replication_slots`, I risk silent data divergence or disk exhaustion due to WAL bloat. A dedicated sentinel class will provide the telemetry needed to ensure my replication topology remains healthy and performant.

## Implementation Steps
1.  **Define `ReplicationSentinel`:** Create `bag/db_sentinel.py` with a method to query `pg_replication_slots` for `restart_lsn` and `confirmed_flush_lsn`.
2.  **Calculate Lag:** Implement logic to convert LSN differences into bytes, providing a clear "lag-in-bytes" metric.
3.  **Threshold Alerting:** Add a configurable threshold; if lag exceeds a defined limit, trigger a log entry or an `_alert_dot` call.
4.  **Integration:** Register the sentinel in the `run_cycle` startup sequence to ensure it runs as a background health check.

## Risk
**Failure Mode:** The sentinel might trigger false positives if the database is under heavy write load, leading to "alert fatigue" or unnecessary rollbacks.
**Mitigation:** Implement a "moving average" window for lag calculation rather than a single-point-in-time check, ensuring alerts only fire on sustained, significant lag.

**Confidence Score: 9/10** (The logic is straightforward, and the system tables are well-documented).