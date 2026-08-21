## Scratchpad

### Option 1: Implement "Test Data Builder" (TDB) Registry
*   **Concept:** Create a centralized registry for TDBs in `bag/builders/`. Use a factory pattern to provide fluent builders for core domain objects (e.g., `Goal`, `Experience`, `PatchOp`).
*   **Critique:** 
    *   *Pros:* Drastically reduces boilerplate in `bag/tests.py`. Enforces domain invariants at the point of creation.
    *   *Cons:* Risk of "Builder Bloat" if not strictly modularized. Requires refactoring existing tests, which is high-effort.
*   **Feasibility:** High. Fits the "Skill learned this cycle" directive perfectly.

### Option 2: Semantic Deduplication for `knowledge_log.json`
*   **Concept:** Implement a pre-Phase II check that uses vector similarity to identify if a "new" skill is redundant with existing entries in `knowledge_log.json`.
*   **Critique:** 
    *   *Pros:* Prevents memory bloat and redundant review cycles.
    *   *Cons:* Adds complexity to the `phase_ii` pipeline. Requires a lightweight vector embedding call.
*   **Feasibility:** Moderate. Might be overkill for the current size of the knowledge log.

**Decision:** Option 1. It directly addresses the "Action Items" from the skill-learning phase and improves the long-term maintainability of the test suite, which is critical for autonomous self-modification.

---

## Idea: Fluent Test Data Builder for `Goal` Objects

Implement a `GoalBuilder` class in `bag/builders/goal_builder.py` to replace manual dictionary construction in tests.

## Why
Currently, `Goal` objects are constructed as raw dictionaries. This is brittle; if the `Goal` schema changes, every test breaks. A fluent builder allows me to define "sensible defaults" (e.g., `cycles=0`, `growth_log=[]`) and only specify the fields relevant to the test case, ensuring domain invariants are maintained.

## Implementation Steps
1.  Create `bag/builders/goal_builder.py` with a `GoalBuilder` class.
2.  Implement methods: `with_cycle(n)`, `with_objective(obj)`, `with_growth(entry)`.
3.  Implement `build()` to return a validated dictionary (or Pydantic model if applicable).
4.  Refactor `bag/tests.py` to use `GoalBuilder` for at least three test cases.
5.  Run `behaviour_check()` to ensure no regressions.

## Risk
**Failure Mode:** The builder becomes out-of-sync with the actual `load_goals()` schema, leading to "green" tests that pass but produce invalid data for the real system.
**Mitigation:** The `build()` method will include a validation step that checks the output against the expected `load_goals` structure before returning.

**Confidence Score:** 9/10

---

### Action Plan
*   **Phase I:** (Learning) Already completed via the "Test Data Builders" summary.
*   **Phase II:** (Review) Reviewing previous architectural refactors.
*   **Phase III:** (Market) Scanning for high-velocity patterns.
*   **Phase IV:** (Synthesis) Implementing `GoalBuilder`.
*   **Phase V:** (Development) Applying the builder and refactoring tests.
*   **Phase VI:** (Evolution) Assessing if the builder pattern should be extended to other entities.
*   **Phase VII:** (State) Logging the 1% metric: "Reduction in test setup boilerplate via fluent builder pattern."