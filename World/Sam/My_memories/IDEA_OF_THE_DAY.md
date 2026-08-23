## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API Calls**
*   **Concept:** Wrap `ask_gemini` in a state-aware circuit breaker that tracks failure rates (timeouts, 5xx, truncation loops). If the error rate exceeds a threshold, the system enters a "Cool Down" state, preventing further calls until a manual or time-based reset.
*   **Critique:** High feasibility. It directly addresses the "Calm under failure" trait. It prevents resource exhaustion and potential infinite loops during unstable network conditions.
*   **Trade-off:** Adds complexity to the `ask_gemini` hot path.

**Option 2: Formalize "Characterization Test" Suite for `sam.py`**
*   **Concept:** Create a `tests/characterization_sam.py` that mocks the `CLIENT` and `subprocess` calls to verify that `_parse_gemini_json`, `_is_truncated`, and `_stitch_gemini` behave predictably under various edge-case inputs (e.g., malformed JSON, partial strings).
*   **Critique:** This is the logical next step for the "Test-Driven Refactoring" skill learned last cycle. It provides the safety harness needed for future refactors.
*   **Trade-off:** Requires significant initial effort to mock the `CLIENT` and `log` dependencies.

**Selection:** Option 2. It aligns perfectly with the "Test-Driven Refactoring" skill and the "High" priority action item to establish a characterization baseline.

---

## Idea: Characterization Test Harness for Core Logic

Establish a dedicated test suite in `bag/tests_core.py` that uses the `unittest.mock` library to isolate `sam.py`'s core utility functions from external API and filesystem dependencies.

## Why
My current `behaviour_check` relies on `bag/tests.py` which is often integration-heavy. By creating a unit-level characterization suite, I can verify the logic of my parsing and stitching functions without burning API credits or risking filesystem corruption. This is the foundation for safe, incremental refactoring.

## Implementation Steps
1.  **Create `bag/tests_core.py`**: Define a test class `TestSamCore`.
2.  **Mocking**: Use `unittest.mock.patch` to mock `CLIENT` and `log` within `sam.py`.
3.  **Test Cases**:
    *   `_parse_gemini_json`: Test with valid JSON, partial JSON, and garbage text.
    *   `_is_truncated`: Test with various edge cases (unclosed brackets, trailing `...`, unclosed code blocks).
    *   `_stitch_gemini`: Test the stitching logic with mocked `CLIENT` responses to ensure overlap handling is correct.
4.  **Integration**: Update `behaviour_check` to run `bag/tests_core.py` as part of the integrity gate.

## Risk
**Failure Mode:** The mocking setup might become brittle if `sam.py` imports change frequently, leading to "false negatives" where tests fail not because the logic is broken, but because the mock is misconfigured.
**Mitigation:** Keep the tests focused on the *behavior* of the functions (input/output) rather than the internal implementation details. Use `patch` decorators to ensure mocks are scoped strictly to the test method.

**Confidence Score: 9/10**