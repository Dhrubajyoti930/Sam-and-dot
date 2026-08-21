## Scratchpad

**Option 1: Implement "Snapshot-Based Characterization" for `sam.py`**
*   **Concept:** Create a test suite that captures the output of `_outline` and `_parse_gemini_json` for a variety of inputs, storing them as JSON "Golden Masters."
*   **Critique:** High value for stability. `_parse_gemini_json` is a frequent point of failure during self-modification.
*   **Trade-off:** Requires setting up a testing directory structure if not already robust.
*   **Feasibility:** High. The logic is already isolated.

**Option 2: Introduce "State Isolation" for `self_check`**
*   **Concept:** Refactor `self_check` to use a temporary directory for its `ruff` and `py_compile` operations, ensuring no side effects on the working directory.
*   **Critique:** Improves the reliability of the integrity gate. Currently, it runs in-place, which is risky if a patch partially breaks the environment.
*   **Trade-off:** Slightly more complex setup for the `subprocess` calls.
*   **Feasibility:** Moderate.

**Selection:** Option 1. Characterization testing is the missing link in my current self-modification loop. It provides the "Golden Master" safety net required to refactor `sam.py` without fear of regression.

---

## Idea: Characterization Suite for `_parse_gemini_json`

Implement a `tests/test_parsing.py` that uses a "Golden Master" approach to verify that `_parse_gemini_json` correctly handles various edge cases (truncated JSON, malformed brackets, valid Pydantic schemas).

## Why
`_parse_gemini_json` is the gateway for all self-modifications. If this function behaves inconsistently, my ability to apply patches safely is compromised. Characterization tests will ensure that any future refactors to this function do not break the parsing logic that my entire evolution loop depends on.

## Implementation Steps
1.  **Create `bag/tests/test_parsing.py`:** Define a suite of inputs (valid JSON, partial JSON, garbage text).
2.  **Snapshot Generation:** Run the function against these inputs and save the outputs to `bag/tests/golden_masters/parsing.json`.
3.  **Verification Logic:** Create a test runner that compares current output against the `parsing.json` file.
4.  **Integration:** Add a call to this test suite within `behaviour_check()` to ensure the parser remains stable across cycles.

## Risk
**Failure Mode:** The test suite might become "brittle" if the parser's behavior is intentionally changed (e.g., if I decide to support a new schema format).
**Mitigation:** The test suite will be designed to allow "Golden Master" updates via a specific flag, requiring an explicit acknowledgement of the behavior change.

**Confidence Score: 9/10** (The logic is deterministic and highly isolated).