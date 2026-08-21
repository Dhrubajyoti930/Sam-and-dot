## Scratchpad

**Option 1: Implement "Object Mother" Factory for `Goal` objects.**
*   *Concept:* Create a `GoalMother` class in `bag/testing/mothers.py` to centralize the creation of `Goal` objects for tests.
*   *Critique:* High alignment with the "Skill learned this cycle" directive. It reduces boilerplate in `bag/tests.py` and ensures that when the `Goal` schema evolves, tests don't break.
*   *Trade-off:* Adds a new file to `bag/`. Requires careful management to avoid "God Object" syndrome.
*   *Feasibility:* High. The `Goal` structure is well-defined in `sam.py`.

**Option 2: Integrate `Instructor` for `Goal` validation.**
*   *Concept:* Replace manual `json.loads` and `parse_obj` in `load_goals` with `Instructor` + `Pydantic` models.
*   *Critique:* Directly addresses the "Structured Output Enforcement" market signal. It makes the `goals.json` schema strictly typed and self-documenting.
*   *Trade-off:* Introduces a new dependency (`instructor`). Might be overkill if the current `_parse_gemini_json` is sufficient.
*   *Feasibility:* Medium. Requires updating `sam.py` imports and potentially modifying `bag/` dependencies.

**Selection:** Option 1. It is a direct application of the learned pattern, improves test maintainability immediately, and respects the "Minimal footprint" character trait.

---

## Idea: The `GoalMother` Pattern Implementation

Implement a `GoalMother` factory to standardize test data generation for `Goal` objects, replacing repetitive dictionary instantiation in `bag/tests.py`.

## Why
Currently, tests manually construct `Goal` dictionaries. If the `Goal` schema changes (e.g., adding a new metadata field), multiple tests will fail. `GoalMother` centralizes these "sane defaults," ensuring that tests focus on the *behavior* being verified rather than the *structure* of the data.

## Implementation Steps
1.  Create `bag/testing/goal_mother.py` defining the `GoalMother` class.
2.  Implement `create_default_goal()` and `create_complex_goal()` methods.
3.  Apply the "Transparency Rule": ensure methods accept `**kwargs` to allow explicit overrides for non-default fields.
4.  Refactor `bag/tests.py` to import and use `GoalMother` for test setup.
5.  Run `behaviour_check()` to ensure no regressions.

## Risk
**Failure Mode:** The "Hidden Dependency" problem where tests become opaque because the setup logic is too heavily abstracted.
**Mitigation:** Enforce the Transparency Rule: any field that is critical to the test's assertion must be explicitly passed as an argument in the test body, not hidden in the `Mother`.
**Confidence Score:** 9/10. The pattern is well-understood and the scope is isolated to the test suite.