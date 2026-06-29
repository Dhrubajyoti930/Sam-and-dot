## Scratchpad

**Option 1: Adaptive Rate-Limiting Middleware**
*   **Concept:** Implement a token-bucket algorithm in `sam.py` that dynamically adjusts `_CALL_DELAY` based on Gemini API response headers (e.g., `X-RateLimit-Remaining`).
*   **Critique:** High feasibility. It moves Sam from static sleep intervals to reactive flow control.
*   **Trade-off:** Increases complexity in `ask_gemini`. Requires parsing headers from the `google-generativeai` response object.
*   **Maintainability:** High. Reduces "429 Too Many Requests" errors, making the system more resilient.

**Option 2: Monotonic Stack Utility Module**
*   **Concept:** Create `bag/algorithms/stack.py` containing a generic `MonotonicStack` class as per the cycle's learned skill.
*   **Critique:** High feasibility. It encapsulates the $O(n)$ logic into a reusable, testable module.
*   **Trade-off:** Minimal. It adds a file to `bag/`, but follows the "modular, not monolithic" philosophy.
*   **Maintainability:** Excellent. Provides a clean API for future performance-critical tasks.

**Selection:** Option 2. It directly applies the learned skill into a reusable component, adhering to the "minimal footprint, maximum leverage" core trait.

---

## Idea: `MonotonicStack` Utility Module

## Why
The monotonic stack pattern is a high-leverage tool for $O(n)$ optimization in data processing. By formalizing this into a dedicated module, I reduce the risk of implementing buggy, ad-hoc loops in future cycles and provide a clean, tested interface for solving "next greater/smaller" problems.

## Implementation Steps
1.  Create `bag/algorithms/stack.py`.
2.  Implement `MonotonicStack` class with a `push(value, index)` method and a `get_nge()` (Next Greater Element) method.
3.  Use a custom comparator function (defaulting to `operator.gt`) to support both "greater" and "smaller" logic.
4.  Add a unit test in `bag/tests.py` to verify $O(n)$ performance and correctness against edge cases (empty, circular, monotonic).

## Risk
**Failure Mode:** The stack logic might be misused for non-linear data structures, leading to incorrect results if the user assumes a standard array input.
**Mitigation:** Add clear docstrings specifying the input requirements (indexable, linear sequence) and include a `validate_input` method that checks for indexability.

**Confidence Score:** 9/10. The logic is well-understood and the implementation is isolated.