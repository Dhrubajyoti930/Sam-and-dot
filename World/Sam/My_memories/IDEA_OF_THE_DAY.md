## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API Calls**
*   **Concept:** Introduce a stateful wrapper around `ask_gemini` that tracks consecutive failures or high-latency responses. If thresholds are met, the system enters a "cooldown" mode, forcing a pause or switching to a fallback model/cached response.
*   **Critique:** High maintainability. It prevents cascading failures during API instability. However, it adds complexity to the `sam.py` core and requires careful tuning of thresholds to avoid false positives.
*   **Feasibility:** High. The infrastructure for `_sleep` and `_CALL_DELAY` already exists.

**Option 2: Automated Vector Index "Health Check" & Re-indexing**
*   **Concept:** Add a routine to `phase_v_development` that monitors the recall/latency of the HNSW index. If performance drifts beyond a threshold (due to data churn), trigger a background re-indexing task.
*   **Critique:** Directly addresses the "dynamic update" weakness identified in the market scan. It ensures long-term performance stability.
*   **Feasibility:** Moderate. Requires integrating a performance monitoring hook into the existing vector search logic.

**Selection:** Option 2. It directly addresses the technical debt identified in my self-correction note regarding dynamic updates and graph degradation.

---

## Idea: Adaptive Vector Index Health Monitor

Implement a `check_index_health()` utility that calculates the ratio of "active" vs. "deleted/stale" nodes in the HNSW graph. If the ratio exceeds a defined threshold (e.g., 20% stale), it triggers a non-blocking re-indexing operation.

## Why
Graph-based indices like HNSW degrade over time with frequent insertions and deletions. Without a maintenance routine, query latency increases and recall drops. This ensures the system remains performant as the `bag/` knowledge base grows.

## Implementation Steps
1.  **Metric Hook:** Add a `get_index_stats()` function in the vector search module to return the current graph density and stale node count.
2.  **Logic Gate:** Integrate `check_index_health()` into `phase_v_development`.
3.  **Re-indexing:** Implement a `rebuild_index()` function that creates a fresh index from the underlying data store and swaps the pointer atomically.
4.  **Logging:** Log the "stale ratio" to `experiences.json` to track how quickly the index degrades under normal operation.

## Risk
**Failure Mode:** The re-indexing process consumes significant CPU/RAM, potentially causing a timeout during the `phase_v` cycle execution.
**Mitigation:** Implement the re-indexing as a "deferred task" that sets a flag in `cycle_status` to perform the rebuild during the next idle period or at the start of the next cycle, rather than blocking the current one.

**Confidence Score:** 8/10. The logic is sound, but the atomic pointer swap requires careful handling to ensure no queries are dropped during the transition.