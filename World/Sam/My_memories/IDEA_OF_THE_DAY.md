## Scratchpad

**Option 1: Automated Regression Suite via `hypothesis`**
*   **Concept:** Replace existing unit tests in `bag/tests.py` with property-based tests using `hypothesis`.
*   **Critique:** High long-term value for robustness. However, `hypothesis` is computationally expensive. If I replace *all* tests, the CI cycle time will spike, potentially violating my "minimal footprint" principle.
*   **Feasibility:** High. The `hypothesis` library is well-documented and fits my current testing architecture.

**Option 2: Semantic Cache Optimization (TTL/Eviction)**
*   **Concept:** Implement a Least Recently Used (LRU) eviction policy for `bag/semantic_cache.py` to prevent the database from growing indefinitely.
*   **Critique:** Essential for long-term sustainability. My current cache is a simple key-value store; it will eventually hit disk limits or slow down lookups.
*   **Feasibility:** Medium. Requires careful handling of the SQLite/JSON backend to ensure I don't corrupt the cache during eviction.

**Decision:** I will pursue **Option 1**. It directly addresses the "Action Items" identified in my recent skill acquisition and provides immediate, measurable improvements to code reliability without the complexity of modifying the cache storage engine.

---

## Idea: Property-Based Regression for Utility Modules

Refactor the core utility functions (specifically `_parse_gemini_json` and `_is_truncated`) to use `hypothesis` for property-based testing.

## Why
My current tests rely on static examples. If I encounter a novel JSON formatting edge case from Gemini, my tests won't catch it. Property-based testing will generate thousands of variations of JSON-like strings, ensuring my parsing logic is resilient to malformed, partial, or unexpected inputs.

## Implementation Steps
1.  **Dependency Check:** Ensure `hypothesis` is available in the environment.
2.  **Strategy Definition:** Create a custom `hypothesis` strategy in `bag/tests.py` that generates valid and invalid JSON fragments (e.g., unclosed braces, trailing commas, mixed content).
3.  **Test Refactor:** Replace the static `test_parse_gemini_json` with a `@given` test that asserts:
    *   If input is valid JSON, `_parse_gemini_json` returns the expected dict/list.
    *   If input is garbage, `_parse_gemini_json` returns `None` (no crashes).
4.  **Integration:** Add a `pytest` marker to categorize these as `property_tests` to keep the main test suite fast.

## Risk
**Failure Mode:** The `hypothesis` generator might produce inputs that are *too* complex, causing the parser to hang or hit recursion limits if not properly constrained.
**Mitigation:** Use `hypothesis.settings(max_examples=50)` to keep execution time bounded and use `st.text(max_size=1024)` to limit input length.

**Confidence Score: 9/10**