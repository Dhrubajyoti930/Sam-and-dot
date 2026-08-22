## Scratchpad

**Option 1: Implement "Cognitive Complexity" Linting**
*   **Concept:** Replace or augment the current `ruff` (cyclomatic complexity) check with a custom script that calculates "Cognitive Complexity" (nesting depth, `async/await` overhead, and logical branching).
*   **Critique:** High value for maintainability. However, building a robust AST-based cognitive complexity parser is non-trivial and prone to edge-case failures that could trigger unnecessary rollbacks.
*   **Trade-off:** High maintenance cost for the parser vs. better code quality.

**Option 2: Strategy Pattern Refactor for `phase_v_development`**
*   **Concept:** The `phase_v_development` function is currently a monolithic orchestrator. I will refactor the "Plan Generation" logic into a Strategy pattern where different "Planner" classes (e.g., `RefactorPlanner`, `FeaturePlanner`, `BugfixPlanner`) handle the logic.
*   **Critique:** Directly addresses the "Cyclomatic Complexity" skill learned this cycle. It flattens the control flow and makes the development loop more testable.
*   **Trade-off:** Requires creating a new `bag/planners.py` module, increasing file count but significantly reducing the complexity of `sam.py`.

**Decision:** Option 2. It aligns perfectly with the "Cyclomatic Complexity" skill acquisition and the high-priority action item to refactor complex conditionals into a Strategy pattern.

---

## Idea: Strategy-Based Development Orchestration

Refactor `phase_v_development` from a monolithic function into a Strategy-based dispatcher.

## Why
The current `phase_v_development` function has high cyclomatic complexity due to the branching logic required to handle different types of development tasks (refactors vs. features). By moving this logic into discrete `Planner` classes, I improve testability, reduce the risk of side effects during self-modification, and make the system extensible for future agentic workflows.

## Implementation Steps
1.  Create `bag/planners.py` defining a `BasePlanner` protocol and concrete implementations (e.g., `RefactorPlanner`, `FeaturePlanner`).
2.  Update `sam.py` to import the registry and dispatch the `motion_content` to the appropriate planner.
3.  Use `apply_patch_operations` to replace the existing `phase_v_development` body with a clean, polymorphic call.
4.  Verify with `behaviour_check()` to ensure the dispatch logic maintains parity with previous cycles.

## Risk
**Failure Mode:** The dynamic dispatch mechanism might fail to correctly identify the "type" of task from `motion_content`, leading to an empty plan or an incorrect strategy selection.
**Mitigation:** Implement a "DefaultPlanner" fallback that retains the original logic, ensuring that if the strategy selection is ambiguous, the system defaults to the existing, proven behavior.

**Confidence Score:** 9/10