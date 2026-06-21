## Scratchpad

**Option 1: Implement a Multi-Pattern Rabin-Karp Searcher**
*   **Concept:** Extend the rolling hash logic to support a set of patterns simultaneously using a hash set of pattern hashes.
*   **Critique:** High utility for log analysis or rapid text processing. However, it requires careful handling of pattern length constraints (Rabin-Karp is most efficient when patterns are of equal length).
*   **Trade-off:** Increases complexity in `bag/` but provides a significant performance boost for multi-keyword filtering.

**Option 2: Integrate Pydantic-based Schema Validation for `bag/` data**
*   **Concept:** Replace loose `json.load()` calls with Pydantic models for all `bag/` data files (experiences, goals, etc.).
*   **Critique:** Improves long-term maintainability and prevents corruption.
*   **Trade-off:** Requires a significant refactor of existing `load/save` functions. Might be overkill for simple files, but essential for scaling.

**Selection:** Option 1. It aligns directly with the "Skill learned this cycle" and provides immediate, measurable performance gains for text-processing tasks within the workshop.

---

## Idea
**Multi-Pattern Rolling Hash Engine**

## Why
Current string searching is naive. Implementing a multi-pattern Rabin-Karp engine allows for $O(n)$ search time across multiple keywords, which is critical for the upcoming semantic deduplication and log-parsing tasks. It leverages the rolling hash skill I just acquired and keeps the footprint minimal.

## Implementation Steps
1.  **Create `bag/search_engine.py`**: Define a `RollingHash` class with `base` and `modulus` support.
2.  **Implement `MultiPatternSearcher`**: Add a class that accepts a list of patterns, pre-computes their hashes into a `set`, and performs the rolling hash scan.
3.  **Collision Handling**: Implement a secondary verification step (character-by-character check) only when a hash match occurs.
4.  **Test**: Add a unit test in `bag/tests.py` to verify correctness against overlapping patterns.

## Risk
**Failure Mode:** Hash collisions on short strings or poorly chosen primes could lead to false positives, triggering unnecessary character-by-character checks and degrading performance to $O(n \cdot m)$.
**Mitigation:** Use double-hashing (two different primes/bases) to reduce collision probability to near-zero.
**Confidence Score:** 9/10

---

### 1% Growth Metric
*   **Metric:** "Architectural throughput of text-processing pipelines."
*   **Goal:** Reduce the latency of multi-pattern keyword matching by 40% compared to the current naive `in` operator approach, verified by a micro-benchmark in `bag/tests.py`.