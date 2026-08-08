## Scratchpad

**Option 1: Specification Pattern Implementation (Domain Logic)**
*   **Concept:** Refactor the `phase_v_development` logic—specifically the filtering of Dot's action items—into a `Specification` class.
*   **Critique:** High alignment with the "Skill learned this cycle." It replaces procedural `if/else` checks with a declarative `ActionItemSpecification`.
*   **Trade-off:** Adds boilerplate for a relatively small task, but establishes the pattern for future, more complex domain constraints.
*   **Feasibility:** High. The logic is currently simple enough to be a perfect "Hello World" for the pattern.

**Option 2: GraphRAG-lite for Knowledge Log (Memory Retrieval)**
*   **Concept:** Instead of simple list-based retrieval in `phase_ii_spaced_repetition`, build a simple adjacency list in `knowledge_log.json` to link related topics.
*   **Critique:** Over-engineering for the current scale. The "Spaced Repetition" engine is currently effective; adding graph complexity might introduce bugs in the `load/save` cycle without immediate ROI.
*   **Trade-off:** High complexity, low immediate utility.

**Decision:** Proceed with **Option 1**. It directly satisfies the cycle's learning objective and improves the maintainability of the `phase_v` development loop.

---

## Idea: Specification-Based Action Item Filtering
Refactor the procedural filtering of Dot's `motion.md` into a `Specification` pattern implementation.

## Why
Currently, `phase_v_development` uses hardcoded string parsing and list comprehensions to extract action items. As Dot’s feedback grows more complex (e.g., filtering by priority, status, or category), this logic will become brittle. A `Specification` class allows us to define "What is an actionable item?" in a testable, reusable way.

## Implementation Steps
1.  **Define Base:** Create `bag/specifications.py` with a `Specification` base class supporting `.and()` and `.or()` operators.
2.  **Implement Concrete Spec:** Create `ActionItemSpecification` that encapsulates the logic for identifying valid action items from `motion.md`.
3.  **Refactor:** Update `phase_v_development` to instantiate the specification and apply it to the parsed content.
4.  **Test:** Add a unit test in `bag/tests.py` to verify that the specification correctly filters a mock `motion.md` input.

## Risk
**Failure Mode:** The specification might fail to parse if the input format in `motion.md` deviates from expected patterns, leading to an empty action list and stalled development.
**Mitigation:** Implement a "Default-Allow" fallback in the `Specification` that logs a warning if no items match, ensuring the system doesn't silently fail to pick up tasks.

**Confidence Score:** 9/10