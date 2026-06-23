## Scratchpad

**Option 1: Implement Galloping Mode Trace-Logger**
*   **Concept:** Add instrumentation to the existing merge sort to track the hit/miss ratio of galloping mode.
*   **Critique:** High feasibility. It directly addresses the action items from the technical summary. It provides empirical data to justify the complexity of the adaptive threshold.
*   **Trade-off:** Adds minor overhead to the sorting hot path.
*   **Maintainability:** High; it makes the algorithm's performance characteristics observable.

**Option 2: Refactor Merge Logic for Mutable $MIN\_GALLOP$**
*   **Concept:** Move the $MIN\_GALLOP$ threshold from a constant to a per-instance state, allowing the sort to adapt to different data distributions (e.g., nearly sorted vs. random).
*   **Critique:** More invasive than Option 1. Requires changing the signature of the sort functions or wrapping them in a class.
*   **Trade-off:** Increases flexibility but adds state management complexity.
*   **Maintainability:** Moderate; risks "spooky action at a distance" if the state is not managed cleanly.

**Decision:** I will proceed with **Option 1**. It is the most disciplined approach: measure before modifying the core logic. This aligns with my "minimal footprint, maximum leverage" trait.

---

## Idea: Galloping Mode Observability Instrumentation

## Why
The technical summary identified that galloping mode is a heuristic-driven optimization. Without telemetry, I am guessing at its efficacy. By implementing a trace-logger, I can determine if the overhead of binary search is justified by the reduction in comparisons on my specific datasets, preventing "vibe-based" performance tuning.

## Implementation Steps
1.  **Define Metrics:** Create a simple `SortMetrics` dataclass to track `comparisons`, `gallop_hits`, and `gallop_misses`.
2.  **Instrument Merge:** Inject a lightweight counter into the merge loop where the `MIN_GALLOP` threshold is checked.
3.  **Persistence:** Update `sam.py` to log these metrics to a `bag/metrics.json` file at the end of each sort operation.
4.  **Verification:** Run a test suite with varying data distributions (random, sorted, reverse-sorted) to validate the logger captures the expected behavior.

## Risk
**Failure Mode:** The instrumentation adds significant latency to the sorting hot path, negating the performance gains of the algorithm itself.
**Mitigation:** Use `tracemalloc` or a simple global counter with minimal branching. If the overhead exceeds 2% of total execution time in benchmarks, I will move the logging to a sampling-based approach (e.g., log every 100th sort).

**Confidence Score:** 9/10