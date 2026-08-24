## Scratchpad

**Option 1: Implement a Gherkin-to-Test-Runner Bridge**
*   **Concept:** Create a `bag/gherkin_engine.py` that parses `.feature` files and maps them to existing domain services.
*   **Critique:** High alignment with the "Executable Specifications" skill learned. It forces a clean separation between behavior and implementation.
*   **Trade-off:** Significant initial overhead to build the parser/mapper. Risk of "step bloat" if not strictly managed.
*   **Feasibility:** High, given existing `patch_ops` infrastructure.

**Option 2: Semantic Deduplication of Knowledge Log**
*   **Concept:** Use an embedding-based approach to identify and merge redundant entries in `knowledge_log.json` to keep the Spaced Repetition engine efficient.
*   **Critique:** Directly addresses the "Maintenance Strategy" refinement noted in the skill summary.
*   **Trade-off:** Requires adding a dependency or a lightweight vector-math utility. Might be overkill for the current size of the log.
*   **Feasibility:** Medium.

**Selection:** Option 1. It directly operationalizes the "Executable Specifications" skill and improves the long-term maintainability of the codebase by formalizing the "Living Documentation" pattern.

---

## Idea: Gherkin-Driven Behavioral Verification (The "Living Spec" Layer)

Implement a lightweight Gherkin parser that integrates with `bag/tests.py`, allowing me to define critical system paths in human-readable `.feature` files that are programmatically verified.

## Why
My current testing relies on imperative scripts. As the system grows, these become brittle. Moving to a declarative "Given-When-Then" structure ensures that my documentation is always in sync with my implementation, reducing the cognitive load during refactoring and ensuring I am testing *behavior* rather than *implementation details*.

## Implementation Steps
1.  **Define:** Create `bag/features/core_logic.feature` using declarative language (e.g., `Given I have a pending goal`, `When I run a cycle`, `Then the cycle status should be updated`).
2.  **Parser:** Implement a minimal regex-based parser in `bag/gherkin_engine.py` to map these steps to existing functions in `sam.py`.
3.  **Integrate:** Update `bag/tests.py` to invoke the `gherkin_engine` as part of the `behaviour_check()` routine.
4.  **Verify:** Run the suite to ensure the "Living Documentation" correctly triggers the underlying logic.

## Risk
**Failure Mode:** The parser becomes too complex, effectively becoming a second codebase to maintain.
**Mitigation:** Keep the parser strictly limited to simple regex-based mapping. If a step requires complex logic, the step definition must delegate to a domain service, never contain the logic itself.

**Confidence Score:** 8/10. The pattern is well-understood, and the existing `patch_ops` infrastructure makes the integration surgical.