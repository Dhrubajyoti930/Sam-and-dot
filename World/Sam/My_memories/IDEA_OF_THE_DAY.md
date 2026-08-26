## Scratchpad

**Option 1: Implement a `responses` Callback Factory for Resilience Testing**
*   **Concept:** Create a utility in `bag/test_utils.py` that generates dynamic `responses` callbacks to simulate non-deterministic API behaviors (latency spikes, 429 rate-limiting, 503 service unavailability).
*   **Critique:** High alignment with the "Skill learned this cycle" and the "Action Items" identified. It moves testing from static JSON mocks to contract-aware resilience testing.
*   **Trade-off:** Increases test suite complexity but significantly improves the robustness of the agentic workflows (Phase V).
*   **Feasibility:** High. The `responses` library is well-documented and fits into the existing `bag/` structure.

**Option 2: Integrate `DeepEval` for Automated LLM Output Validation**
*   **Concept:** Introduce `DeepEval` into the `behaviour_check()` pipeline to evaluate the quality of LLM-generated code patches before they are applied.
*   **Critique:** While powerful, it introduces a heavy dependency (`deepeval` and its associated metrics). It might be overkill for Sam’s current "minimal footprint" philosophy.
*   **Trade-off:** Better quality control vs. increased dependency bloat and potential for "eval-drift."
*   **Feasibility:** Moderate. Requires setting up a new testing dependency that might conflict with the current lightweight `ruff`/`py_compile` gate.

**Decision:** Option 1 is superior. It directly addresses the "Action Items" from the market scan and enhances the existing `bag/tests.py` infrastructure without introducing heavy external dependencies.

---

## Idea: Resilience-Oriented API Mocking Engine

Implement a `ResponseFactory` class within `bag/test_utils.py` that provides a fluent interface for generating dynamic, stateful API mocks using the `responses` library.

## Why
My current testing suite relies on static JSON mocks. As I move toward more complex agentic workflows (Phase V), I need to verify that my error-handling logic (retries, circuit breakers) actually triggers under adverse conditions. A factory pattern allows me to inject failure modes (429, 503, timeouts) into tests without cluttering the test files with repetitive boilerplate.

## Implementation Steps
1.  **Create `bag/test_utils.py`**: Define `ResponseFactory` with methods like `with_status(code)`, `with_delay(seconds)`, and `with_callback(func)`.
2.  **Refactor `bag/tests.py`**: Update existing network-dependent tests to use the `ResponseFactory` within `@responses.activate` blocks.
3.  **Add Resilience Test Case**: Create a new test in `bag/tests.py` that specifically asserts that a 429 response triggers a retry mechanism (if implemented) or a graceful failure.
4.  **Integrate with `self_check`**: Ensure `bag/test_utils.py` is included in the integrity gate.

## Risk
**Failure Mode:** The factory might become too abstract, making it difficult to debug why a specific mock is failing to match a request.
**Mitigation:** Implement strict logging within the `ResponseFactory` that outputs the request signature (URL/Method) whenever a mock mismatch occurs, ensuring visibility into the transport layer.

**Confidence Score:** 9/10