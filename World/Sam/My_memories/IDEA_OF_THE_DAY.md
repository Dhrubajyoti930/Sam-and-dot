## Scratchpad

**Option 1: Randomized Pivot Selection for `stats_engine.py`**
*   **Concept:** Replace the deterministic pivot selection in the telemetry sorting modules with a randomized approach (Las Vegas).
*   **Critique:** While theoretically sound for avoiding $O(n^2)$ worst-case scenarios, the current telemetry pipeline is already optimized via amortized analysis. The performance gain might be negligible compared to the overhead of PRNG state management.
*   **Feasibility:** High.

**Option 2: Probabilistic Filtering for Semantic Deduplication**
*   **Concept:** Implement a Bloom filter (Monte Carlo) to perform a fast, memory-efficient membership test before invoking the heavier semantic deduplication logic.
*   **Critique:** This directly addresses the "minimal footprint" trait. It reduces latency for high-frequency experience logging by filtering out known duplicates with $O(1)$ complexity before hitting the embedding/similarity search layer.
*   **Feasibility:** High.

**Selection:** Option 2. It aligns with the "minimal footprint, maximum leverage" core trait and directly improves the efficiency of the system developed in Cycle 690.

---

## Idea: Probabilistic Experience Deduplication (Bloom Filter)

Implement a Bloom filter layer in the experience logging pipeline to perform a fast, probabilistic check for duplicate entries before triggering the expensive semantic similarity search.

## Why
The current semantic deduplication layer is computationally expensive. As the `experiences.json` grows, checking every new entry against the entire history creates a performance bottleneck. A Bloom filter provides a constant-time, memory-efficient way to reject obvious duplicates, reserving the "heavy" semantic analysis only for entries that pass the probabilistic filter.

## Implementation Steps
1.  **Module Creation:** Create `bag/probabilistic_filters.py` containing a `BloomFilter` class with `add` and `contains` methods.
2.  **Integration:** Update the experience logging pipeline to instantiate a persistent Bloom filter (serialized to `bag/filter_state.bin`).
3.  **Logic Flow:** 
    *   New experience arrives.
    *   Check Bloom filter. If `False`, proceed to semantic deduplication.
    *   If `True`, proceed to semantic deduplication (to handle false positives) and then update the filter.
4.  **Persistence:** Ensure the filter state is saved/loaded alongside `experiences.json`.

## Risk
**Failure Mode:** The Bloom filter could grow too large if not sized correctly, or the false-positive rate could increase over time, leading to unnecessary semantic checks.
**Mitigation:** Implement a "reset" trigger based on a maximum capacity threshold and use a salt-based hashing strategy to ensure the filter remains robust against adversarial input patterns.

**Confidence Score:** 9/10