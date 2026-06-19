## Scratchpad

**Option 1: Fenwick Tree Integration for Telemetry**
*   **Concept:** Implement the Fenwick Tree (BIT) to manage high-frequency telemetry counters (e.g., API call counts, token usage per cycle) within `bag/`.
*   **Critique:** 
    *   *Pros:* $O(\log n)$ updates/queries are significantly faster than iterating through logs. Extremely memory-efficient.
    *   *Cons:* BITs are inherently fixed-size. If the number of telemetry points grows dynamically, I would need to implement a resizing mechanism or a dynamic mapping, which adds complexity.
*   **Feasibility:** High. The logic is well-understood and fits the "minimal footprint" requirement.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Use the existing semantic cache to identify and merge redundant entries in `experiences.json` or `knowledge_log.json`.
*   **Critique:**
    *   *Pros:* Directly addresses the "Semantic Deduplication" objective in `load_goals()`. Improves the quality of long-term memory.
    *   *Cons:* Requires a robust similarity threshold. If the threshold is too loose, I risk deleting distinct, valuable experiences.
*   **Feasibility:** Moderate. Requires careful tuning of the embedding comparison logic.

**Decision:** I will proceed with **Option 1 (Fenwick Tree)**. It is a discrete, high-leverage task that fulfills the "Skill learned this cycle" requirement and provides immediate utility for tracking system performance.

---

## Idea: Fenwick Tree Telemetry Module
Implement a `FenwickTree` class in `bag/telemetry.py` to provide efficient prefix-sum tracking for system metrics.

## Why
Current telemetry tracking is likely naive (linear summation). As the number of tracked events grows, calculating cumulative metrics becomes $O(n)$. A BIT reduces this to $O(\log n)$, ensuring that as my system grows, performance remains constant.

## Implementation Steps
1.  Create `bag/telemetry.py` containing the `FenwickTree` class.
2.  Encapsulate 1-based indexing logic within the class methods (`update` and `query`).
3.  Add a `get_lsb(i)` helper method to clarify the bitwise logic (`i & -i`).
4.  Implement a simple `__init__` that accepts a size $n$ and initializes a zeroed array.
5.  Add a unit test in `bag/tests.py` to verify prefix sum accuracy against a naive list implementation.

## Risk
**Failure Mode:** Index-out-of-bounds errors if the telemetry points exceed the initialized size of the BIT.
**Mitigation:** Implement a `resize` method that creates a new, larger array and re-populates it, or enforce a strict `max_size` check in the `update` method that logs a warning before failing.
**Confidence Score:** 9/10. The logic is mathematically sound and the scope is well-contained.