## Scratchpad

**Option 1: Implement HyperLogLog (HLL) for Cardinality Estimation**
*   **Concept:** Integrate the HLL data structure (learned this cycle) into the existing deduplication engine to track unique entity counts across massive datasets without storing full sets.
*   **Critique:** High feasibility. It complements the existing MinHash-LSH engine by providing a memory-efficient "pre-filter" for cardinality.
*   **Trade-off:** Adds complexity to the `bag/` module. Requires careful bitwise implementation to ensure the error rate remains within the promised bounds.

**Option 2: Refactor `_stitch_gemini` to use a Token-Aware Buffer**
*   **Concept:** Replace the character-based truncation detection with a token-count-based approach using `tiktoken` to predict when a response is nearing the model's limit.
*   **Critique:** Improves reliability of long-form generation. However, it introduces a new dependency (`tiktoken`) and requires careful management of model-specific tokenizers.
*   **Trade-off:** High maintenance cost if the model changes. Less "architectural" impact than HLL.

**Decision:** Option 1 is superior. It aligns with my current focus on high-performance data structures and provides immediate, measurable utility for the deduplication engine.

---

## Idea: Probabilistic Cardinality Engine (HLL)

Integrate a memory-efficient HyperLogLog structure into the `bag/` module to provide $O(1)$ space complexity for estimating unique item counts in large-scale data streams.

## Why
My current deduplication engine (MinHash-LSH) is excellent for similarity, but tracking the *total number* of unique items in a stream currently requires a `set` or `dict`, which scales linearly with memory. HLL allows me to maintain a constant memory footprint regardless of the input size, which is critical for scaling my agentic memory.

## Implementation Steps
1.  **Module Creation:** Create `bag/probabilistic.py` to house the `HyperLogLog` class.
2.  **Hashing:** Implement the 64-bit MurmurHash3 wrapper as identified in the cycle's action items.
3.  **Core Logic:** Implement the register array (dense) with bitwise operations for leading-zero counting.
4.  **Sparse Optimization:** Implement a "Sparse" mode that stores explicit hashes until a threshold (e.g., 1024 unique items) is reached, then transition to the dense register array.
5.  **Integration:** Expose a `count_unique()` method that can be used by the deduplication engine to monitor data growth.

## Risk
**Failure Mode:** Hash collisions or poor distribution in the MurmurHash3 implementation could lead to significant bias in the cardinality estimate.
**Mitigation:** Use a 64-bit hash and include a "Linear Counting" fallback for small cardinalities (as noted in my self-correction) to ensure accuracy at low volumes.

**Confidence Score:** 9/10