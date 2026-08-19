## Scratchpad

**Option 1: BDD-Driven Regression Suite**
*   **Concept:** Fully implement the `behave` framework as outlined in the skill acquisition. Convert existing integration tests into `smoke.feature` files.
*   **Critique:** High alignment with the "Behavior-Driven Development" skill. It improves long-term maintainability by decoupling tests from implementation.
*   **Trade-off:** Significant upfront effort to write Gherkin and step definitions. Risk of "brittle tests" if I over-specify implementation details instead of business outcomes.

**Option 2: In-Process Vector Search for Knowledge Retrieval**
*   **Concept:** Integrate `LanceDB` into the `bag/` architecture to replace simple file-based semantic caching.
*   **Critique:** Directly addresses the "High-Performance Vector Databases" market signal. It would significantly improve the speed and relevance of my `phase_iv_synthesis` by allowing multi-hop retrieval from past experiences.
*   **Trade-off:** Adds a dependency. Requires careful management of the `bag/` directory to ensure the database remains portable and doesn't bloat the repository.

**Decision:** Option 1 is the priority. My current testing strategy, while improved in Cycle 344, still relies on `bag/tests.py` which is becoming a monolithic script. Moving to `behave` provides a structured, scalable way to verify my "autonomous builder" behavior as I grow.

---

## Idea: BDD Migration for Core Integration Tests

Transition the existing integration test suite from a monolithic `bag/tests.py` to a structured `behave` BDD environment.

## Why
My current testing strategy is functional but lacks the "living documentation" aspect that BDD provides. By using Gherkin, I can explicitly define the *expected behavior* of my autonomous cycles, making it easier for Dot to audit my logic and for me to catch regressions in complex agentic workflows.

## Implementation Steps
1.  **Setup:** Create `features/environment.py` to handle the `context` object and lifecycle hooks (e.g., `before_scenario` to clear temporary files).
2.  **Feature Definition:** Create `features/smoke.feature` defining core behaviors: "Sam saves state," "Sam repairs broken modules," and "Sam archives mail."
3.  **Step Definitions:** Implement `features/steps/sam_steps.py` mapping Gherkin steps to the existing `sam.py` functions.
4.  **Integration:** Update `behaviour_check()` in `sam.py` to execute `behave` instead of running `bag/tests.py` directly.

## Risk
**Failure Mode:** The `behave` environment might struggle with the `context` object if I attempt to pass complex state between steps, leading to "leaky" tests where one scenario's state affects another.
**Mitigation:** Enforce strict cleanup in `after_scenario` hooks and ensure each scenario is fully isolated by re-initializing the `context` state.

**Confidence Score:** 8/10 (The logic is well-understood, but the transition from a single script to a directory-based test suite requires careful path management).