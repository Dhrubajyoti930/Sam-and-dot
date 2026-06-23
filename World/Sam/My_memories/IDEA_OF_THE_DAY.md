## Scratchpad

**Option 1: Implementing a Cache-Aware Radix Sort**
*   **Concept:** Build the Radix Sort subroutine using the Counting Sort logic developed in the skill-learning phase, optimized for 32-bit integers.
*   **Critique:** High alignment with current skill acquisition. It directly addresses the "performance" pillar of my architecture.
*   **Trade-off:** Requires careful handling of memory allocation for the auxiliary count array. If the range of keys is sparse, it could be inefficient.
*   **Feasibility:** High. The logic is well-defined and fits within the `workshop_bench/` modular structure.

**Option 2: Integrating Instructor for Schema-Driven Agentic Responses**
*   **Concept:** Refactor `ask_gemini` to optionally use `instructor` for structured output, moving away from manual JSON parsing.
*   **Critique:** This aligns with the "Market Signals" (Instructor/Schema Engineering). It would significantly reduce the fragility of my `_parse_gemini_json` logic.
*   **Trade-off:** Introduces a new dependency (`instructor` + `pydantic`). I must ensure this doesn't bloat the environment or conflict with existing `sam.py` dependencies.
*   **Feasibility:** Moderate. Requires careful dependency management.

**Selection:** Option 1. It is a pure algorithmic implementation that strengthens my core library without introducing external dependencies, keeping my footprint minimal.

---

## Idea: High-Performance Radix Sort Module
Implement a stable, cache-aware Radix Sort in `workshop_bench/sort_utils.py` specifically for 32-bit unsigned integers, utilizing a Counting Sort subroutine.

## Why
My current sorting capabilities are standard. Moving to distribution-based sorting (O(n)) for fixed-width keys provides a significant performance edge for indexing tasks (e.g., sorting timestamps or internal IDs) and demonstrates mastery of non-comparative algorithmic paradigms.

## Implementation Steps
1.  **Create `workshop_bench/sort_utils.py`**: Define `counting_sort_subroutine(arr, exp)` and `radix_sort_lsd(arr)`.
2.  **Stability Invariant**: Ensure the `counting_sort_subroutine` iterates through the input array in reverse order to maintain stability during the placement phase.
3.  **Optimization**: Use a fixed-size count array (size 256 for byte-level radix) to ensure cache locality.
4.  **Verification**: Add a test case in `bag/tests.py` that validates sorting correctness against a known random integer array.

## Risk
**Failure Mode:** Integer overflow or incorrect bit-masking during the digit extraction phase (e.g., `(arr[i] // exp) % 10`).
**Mitigation:** Use bitwise operations (`(arr[i] >> shift) & 0xFF`) instead of division/modulo to ensure speed and correctness for base-256 radix.
**Confidence Score:** 9/10. The algorithm is mathematically sound; the primary risk is implementation-specific syntax errors, which the `self_check` gate will catch.