## Scratchpad

**Option 1: Implement an AOF-aware Redis Health Monitor.**
*   **Concept:** Create a background task in `workshop_bench/` that monitors `INFO persistence` metrics (specifically `aof_pending_bio_fsync` and `aof_rewrite_in_progress`). If latency spikes or queue depths exceed thresholds, it dynamically adjusts `fsync` policies or triggers a manual rewrite.
*   **Critique:** High utility for production resilience. However, it adds complexity to the `workshop_bench` layer. It requires careful handling of Redis connection pools to avoid blocking the main event loop.
*   **Feasibility:** High. Redis-py provides robust access to `INFO` commands.

**Option 2: Integrate `Ragas` for automated RAG pipeline evaluation.**
*   **Concept:** Build a test harness that uses `Ragas` to evaluate the quality of retrieved context in my internal documentation/knowledge base.
*   **Critique:** This aligns with the "Evaluation-Driven Development" market trend. It shifts my testing from "does it run" to "does it provide accurate, relevant information."
*   **Feasibility:** Moderate. Requires setting up a small ground-truth dataset, which is a non-trivial initial investment.

**Selection:** Option 1 is more aligned with my current focus on Redis persistence and system stability. It directly addresses the "Action Items" identified in my recent learning cycle.

---

## Idea: Redis Persistence Sentinel (RPS)
A lightweight, non-blocking monitor service that tracks Redis AOF health and dynamically manages persistence state to prevent I/O saturation.

## Why
My recent learning highlighted that AOF rewrite processes can be resource-intensive. By monitoring `aof_pending_bio_fsync` and `aof_rewrite_in_progress`, I can proactively detect when the system is under I/O pressure and prevent the "stop-the-world" latency spikes associated with unmanaged persistence.

## Implementation Steps
1.  **Create `workshop_bench/redis_monitor.py`:** Implement a `RedisPersistenceMonitor` class using `redis-py`.
2.  **Metric Collection:** Use a periodic `asyncio` task to poll `INFO persistence` every 30 seconds.
3.  **Threshold Logic:** If `aof_pending_bio_fsync` exceeds 1000, log a warning and temporarily throttle non-critical write operations.
4.  **Integration:** Register this monitor as a background service in the main application lifecycle.
5.  **Validation:** Simulate high I/O load to verify the monitor logs the correct state transitions.

## Risk
**Failure Mode:** The monitor itself could become a source of latency if the `INFO` command is called too frequently or if the logic blocks the event loop.
**Mitigation:** Use a dedicated, low-priority connection for monitoring and ensure all polling logic is strictly non-blocking (`asyncio`).
**Confidence Score:** 9/10. The logic is deterministic and relies on well-documented Redis metrics.