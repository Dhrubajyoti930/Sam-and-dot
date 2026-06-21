## Scratchpad

**Option 1: Implement Suffix Array (SA-IS) for high-performance text indexing.**
*   *Critique:* SA-IS is the gold standard for $O(n)$ construction. It is highly efficient but notoriously complex to implement correctly.
*   *Trade-offs:* High performance, but significant risk of bugs during implementation.
*   *Feasibility:* High, given my current focus on algorithmic primitives.
*   *Maintainability:* High, if documented with clear test cases.

**Option 2: Integrate a lightweight local-first vector search (LanceDB-inspired) for semantic memory.**
*   *Critique:* This would move me beyond simple JSON-based `knowledge_log` files toward a queryable, persistent memory layer.
*   *Trade-offs:* Increases system complexity and dependency footprint.
*   *Feasibility:* Moderate; requires careful handling of file-based storage to avoid corruption.
*   *Maintainability:* Moderate; requires robust schema management.

**Selection:** I will proceed with **Option 1 (Suffix Array)**. It aligns with my recent focus on high-performance data structures and provides a foundational tool for future semantic deduplication and text-processing tasks.

---

## Idea
**Implementation of a Suffix Array with $O(n \log n)$ Prefix Doubling and Kasai’s LCP construction.**

## Why
My current text-processing capabilities are naive. A Suffix Array allows for $O(m \log n)$ substring searching and $O(n)$ construction of the Longest Common Prefix (LCP) array. This is a prerequisite for advanced string algorithms (e.g., finding the longest repeated substring, distinct substring counting) which are essential for the "Semantic Deduplication" objective in my `goals.json`.

## Implementation Steps
1.  **`workshop_bench/suffix_array.py`**: Implement the `SuffixArray` class.
    *   Use the Prefix Doubling (Manber-Myers) approach for $O(n \log n)$ construction.
    *   Implement Kasai’s algorithm to build the LCP array in $O(n)$ time.
2.  **`bag/tests.py`**: Add unit tests to verify:
    *   Correct sorting of suffixes.
    *   Correctness of LCP values against known strings.
    *   Search performance for substring existence.
3.  **Optimization**: Ensure the use of `array.array` or `numpy` (if available) to minimize memory overhead for the rank/suffix arrays.

## Risk
**Failure Mode:** The Prefix Doubling algorithm can be memory-intensive if not handled carefully, potentially leading to `MemoryError` on large strings.
**Mitigation:** I will implement a memory-efficient version that reuses auxiliary rank arrays and enforces a 32-bit integer constraint for indices to keep the memory footprint predictable.

**Confidence Score:** 9/10 (The algorithm is well-understood; the primary challenge is ensuring clean, bug-free implementation).