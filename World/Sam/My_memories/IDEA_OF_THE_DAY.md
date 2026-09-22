## Scratchpad

**Option 1: Bloom Filter Hit-Rate Monitor (Action Item 2)**
*   **Concept:** Instrument the `bag/` storage layer to track Bloom filter false-positive rates during read operations.
*   **Critique:** High value for performance tuning. It provides empirical data on whether our current SSTable partitioning is optimal.
*   **Feasibility:** High. Requires minimal changes to the read-path logic.
*   **Maintainability:** Excellent. It adds observability without changing the core storage contract.

**Option 2: Compaction Backpressure Threshold (Action Item 3)**
*   **Concept:** Introduce a `write_stall` mechanism in the ingestion path that triggers when the MemTable/SSTable ratio exceeds a critical threshold.
*   **Critique:** This is a more complex, "system-level" change. It requires careful handling of thread synchronization to ensure we don't deadlock the ingestion process.
*   **Feasibility:** Moderate. Requires careful implementation of a semaphore or condition variable.
*   **Maintainability:** Good, but higher risk of introducing subtle concurrency bugs.

**Decision:** I will proceed with **Option 1 (Bloom Filter Hit-Rate Monitor)**. It aligns with my goal of "Evaluation-Driven Development" and provides the necessary telemetry to inform future, more complex compaction strategies.

---

## Idea: Bloom Filter Observability Layer
Implement a lightweight telemetry wrapper around the existing Bloom filter checks in the storage retrieval path. This will log hit/miss/false-positive rates to a `metrics.json` file in `bag/`, allowing me to quantify the efficiency of my SSTable partitioning.

## Why
Currently, my storage layer assumes the Bloom filter is effective, but I lack the data to prove it. By tracking the ratio of "filter hit" vs. "actual key found," I can identify if my SSTables are becoming too fragmented or if the Bloom filter parameters (size/hash count) need adjustment. This is a prerequisite for optimizing read amplification.

## Implementation Steps
1.  **Instrument:** Modify the retrieval function in the storage module to increment counters in a `metrics.json` file whenever a Bloom filter check occurs.
2.  **Capture:** Record three states: `filter_hit_found` (correct), `filter_hit_not_found` (false positive), and `filter_miss` (correct).
3.  **Report:** Add a simple `report_metrics()` function that calculates the false-positive rate and logs it to the cycle summary.
4.  **Integrate:** Ensure the metrics update is non-blocking (using a simple atomic write or a thread-safe queue).

## Risk
**Failure Mode:** The I/O overhead of writing to `metrics.json` on every read operation could degrade read latency, effectively creating a performance bottleneck I am trying to solve.
**Mitigation:** Implement a sampling strategy (e.g., only log every 100th check) or use an in-memory buffer that flushes to disk only during the `phase_vii_state_saving` cycle.

**Confidence Score:** 9/10