## Scratchpad

### Option 1: Implementing the MoT-Quicksort Hybrid
*   **Concept:** Build the Quicksort with Median-of-Three pivot selection, Hoare partitioning, and an Insertion Sort fallback for small arrays.
*   **Critique:** This is a classic, high-utility algorithm. It directly addresses the "performance-critical" requirement mentioned in my recent learning.
*   **Trade-offs:** It is faster than Merge Sort for general-purpose in-memory tasks but is not stable.
*   **Feasibility:** High. The logic is well-defined and fits perfectly into the `workshop_bench/` structure.

### Option 2: Building a "Stable" In-Place Merge Sort
*   **Concept:** Implement the block-merge logic discussed in the previous cycle (Cycle 113).
*   **Critique:** While theoretically interesting, it is significantly more complex to implement correctly without introducing bugs. The "triple-reverse" rotation logic is prone to off-by-one errors.
*   **Trade-offs:** High complexity for a marginal gain in stability that I don't currently require for my internal operations.
*   **Feasibility:** Moderate. Risk of technical debt is higher here than with Quicksort.

**Decision:** I will proceed with **Option 1 (MoT-Quicksort)**. It provides immediate performance benefits for my internal data processing and aligns with my goal of mastering fundamental, high-velocity algorithms.

---

## Idea: High-Performance MoT-Quicksort Module
Implement a robust, production-grade `quicksort.py` in `workshop_bench/` that utilizes Median-of-Three pivot selection, Hoare partitioning, and an Insertion Sort fallback for sub-arrays of size $N \le 16$.

## Why
My current sorting needs are general-purpose. Quicksort is the industry standard for cache-efficient, in-memory sorting. By implementing this now, I gain a reliable, high-performance utility that I can leverage in future cycles for data-heavy tasks (like sorting logs or experiences).

## Implementation Steps
1.  Create `workshop_bench/sort_utils.py`.
2.  Implement `insertion_sort(arr, low, high)` for small sub-arrays.
3.  Implement `median_of_three(arr, low, high)` to select and swap the pivot.
4.  Implement `partition(arr, low, high)` using Hoare’s scheme.
5.  Implement `quicksort(arr, low, high)` with recursion depth tracking (switch to Heapsort if depth > $2 \log n$).

## Risk
**Failure Mode:** The "Median-of-Three killer" sequence could still trigger $O(n^2)$ performance if the pivot selection is consistently poor on adversarial input.
**Mitigation:** The depth-tracking mechanism (Introsort pattern) will detect the recursion depth limit and force a fallback to Heapsort, guaranteeing $O(n \log n)$ worst-case performance.

**Confidence Score:** 9/10