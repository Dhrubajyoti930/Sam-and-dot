## Scratchpad

**Option 1: Implement a Thread-Safe 2D BIT Wrapper**
*   **Concept:** Wrap the 2D BIT in a class using `threading.RLock` to allow concurrent updates/queries.
*   **Critique:** While this addresses the concurrency concern noted in my self-correction, it introduces significant lock contention. In a high-throughput environment, the overhead of the lock will likely exceed the $O(\log N \log M)$ performance gains.
*   **Feasibility:** High.
*   **Maintainability:** Moderate; adds complexity to the data structure.

**Option 2: Sparse 2D BIT using `collections.defaultdict`**
*   **Concept:** Replace the dense `bit[N+1][M+1]` array with a `defaultdict(lambda: defaultdict(int))` to handle sparse grids.
*   **Critique:** This solves the memory-prohibitive nature of dense BITs for large, sparse coordinate spaces. It trades a small constant factor in time complexity for massive memory savings. It aligns with my goal of "minimal footprint, maximum leverage."
*   **Feasibility:** High.
*   **Maintainability:** High; simplifies initialization and removes the need for fixed grid dimensions.

**Selection:** Option 2 is superior. It transforms the BIT from a rigid, memory-heavy structure into a flexible, production-ready utility that handles arbitrary coordinate ranges without pre-allocation.

---

## Idea: Sparse 2D Binary Indexed Tree (BIT) Implementation

Implement a `SparseBIT2D` class using nested `defaultdict` structures to enable efficient prefix sum queries on sparse, dynamic 2D grids.

## Why
Standard 2D BITs require $O(N \times M)$ space, which is impractical for large coordinate spaces (e.g., sparse event logs or spatial data). A sparse implementation allows for dynamic growth and memory efficiency while maintaining the $O(\log N \log M)$ update and query complexity.

## Implementation Steps
1.  **Define Structure:** Create `SparseBIT2D` class using `collections.defaultdict(lambda: defaultdict(int))` for the internal tree storage.
2.  **Update Logic:** Implement `update(x, y, delta)` using the standard BIT propagation: `while i <= MAX: ... while j <= MAX: ...`.
3.  **Query Logic:** Implement `query(x, y)` using the standard BIT traversal: `while i > 0: ... while j > 0: ...`.
4.  **Range Query:** Implement `query_range(x1, y1, x2, y2)` using the 2D inclusion-exclusion principle.
5.  **Validation:** Add a test case in `bag/tests.py` verifying that the sparse implementation matches the results of a brute-force 2D array for small, sparse datasets.

## Risk
**Failure Mode:** The use of `defaultdict` introduces a slight overhead compared to contiguous memory arrays, which may impact performance in extremely dense, high-frequency update scenarios.
**Mitigation:** If performance profiling shows excessive overhead, I will implement a "hybrid" approach where the structure uses a flat array for known dense regions and `defaultdict` for sparse overflow.

**Confidence Score:** 9/10