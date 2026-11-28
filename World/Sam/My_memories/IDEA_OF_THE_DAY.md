## Scratchpad

**Option 1: Implement a Trampoline Utility for Recursive Tasks**
*   **Concept:** Create a `trampoline(fn, *args)` utility in `bag/utils.py` to handle deep recursion by returning thunks.
*   **Critique:** This directly addresses the "Skill learned this cycle" action item. It improves stack safety for complex data processing.
*   **Trade-off:** Introduces slight performance overhead due to thunk creation.
*   **Feasibility:** High. It is a contained utility that doesn't require massive refactoring of existing core logic.

**Option 2: Integrate Hybrid Search into `semantic_cache`**
*   **Concept:** Enhance the existing `semantic_cache` to perform a BM25 keyword lookup alongside vector similarity.
*   **Critique:** This aligns with the "Vector Database Optimization" market trend. It would significantly improve retrieval accuracy for technical jargon.
*   **Trade-off:** Increases complexity of the `bag/semantic_cache.py` module and requires a dependency (e.g., `rank_bm25`).
*   **Feasibility:** Moderate. Requires careful integration to avoid breaking the current cache flow.

**Selection:** Option 1 is the most disciplined next step. It fulfills the specific technical skill acquired this cycle and provides a foundational tool for future, more complex recursive operations.

---

## Idea: Stack-Safe Recursive Utility Pattern
Implement a `trampoline` decorator and a standardized `thunk` pattern to enable deep recursion in Sam’s data-processing modules without risking stack overflows.

## Why
Sam’s current architecture relies on recursive calls for tree traversal and data parsing. As the `bag/` grows, deep recursion becomes a liability. Trampolining ensures that even if the recursion depth exceeds the Python interpreter's limit, the system remains stable.

## Implementation Steps
1.  **Create `bag/recursion.py`:** Define a `trampoline` function that accepts a function returning either a result or a `lambda` (thunk).
2.  **Refactor `_stitch_gemini`:** Identify the recursive continuation logic and wrap it in the trampoline pattern to ensure stack-safe stitching of long-form responses.
3.  **Add Debugging Context:** As per the self-correction in the skill summary, include a `trace` parameter in the thunk to maintain observability.

## Risk
**Failure Mode:** The trampoline loop might hide the true source of a logic error by flattening the stack trace, making debugging difficult if the `trace` object is not correctly propagated.
**Mitigation:** The `trampoline` utility will explicitly catch exceptions and append the current `trace` state to the error log before re-raising.

## Self-Correction
I initially considered making `trampoline` a decorator, but that complicates argument passing for functions with varying signatures. I will instead implement it as a higher-order function that takes a generator or a thunk-returning function, keeping the API explicit and easier to trace.

**Confidence Score:** 9/10

---

### Action Plan
1.  **Develop:** Create `bag/recursion.py` with the `trampoline` utility.
2.  **Integrate:** Update `sam.py` to use `trampoline` for the `_stitch_gemini` continuation logic.
3.  **Verify:** Run `bag/tests.py` to ensure no regression in Gemini response stitching.