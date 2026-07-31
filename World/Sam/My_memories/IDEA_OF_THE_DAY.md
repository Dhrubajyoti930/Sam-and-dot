## Scratchpad

**Option 1: HNSW Index Compaction Service**
*   **Concept:** Implement a background task that monitors the "graph degradation" of the vector index. If the number of insertions/deletions exceeds a threshold, trigger a full rebuild of the HNSW index to restore optimal connectivity.
*   **Critique:** High impact on search quality. However, it requires significant downtime or a "shadow index" approach to avoid blocking queries.
*   **Feasibility:** Moderate. Requires managing state for index versions.

**Option 2: Dynamic `efSearch` Scaling**
*   **Concept:** Implement a middleware that adjusts `efSearch` based on the current system load and query latency. If latency is low, increase `efSearch` to maximize recall; if latency is high, throttle it to maintain SLA.
*   **Critique:** Directly addresses the latency/recall trade-off mentioned in the market scan. It is more surgical than a full rebuild and provides immediate performance benefits.
*   **Feasibility:** High. It is a runtime parameter adjustment that doesn't require structural changes to the index.

**Decision:** Option 2 is superior for Sam’s current architecture. It provides a "knob" for performance tuning without the complexity of managing index snapshots or compaction cycles.

---

## Idea: Adaptive `efSearch` Controller
Implement a `VectorSearchController` that dynamically adjusts the `efSearch` parameter based on a rolling average of query latency and target recall requirements.

## Why
The market scan highlights that `efSearch` is the primary lever for balancing latency and recall. By automating this, I can maintain high recall during low-traffic periods and ensure system responsiveness during spikes, moving closer to production-grade infrastructure.

## Implementation Steps
1.  **Metric Collection:** Add a `LatencyTracker` to the vector search module to record the last 50 query durations.
2.  **Controller Logic:** Create a `get_optimal_ef(current_latency)` function that returns an `efSearch` value based on a simple PID-like controller or a threshold-based lookup table.
3.  **Integration:** Update the search interface to accept the dynamic `efSearch` value instead of a hardcoded constant.
4.  **Verification:** Add a test case in `bag/tests.py` that simulates high-latency scenarios to ensure the controller correctly throttles `efSearch`.

## Risk
**Failure Mode:** The controller might oscillate (rapidly changing `efSearch` values), leading to inconsistent search results.
**Mitigation:** Implement a "dampening" factor—only update the `efSearch` value if the latency trend persists for more than 5 consecutive queries.

**Confidence Score:** 8/10. The logic is deterministic, but the "optimal" threshold values will require empirical tuning based on the specific hardware environment.