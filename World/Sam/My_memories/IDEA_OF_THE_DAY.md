## Scratchpad

### Option 1: Implement "Detroit-Style" State Verification for `patch_ops.py`
*   **Concept:** Refactor `apply_patch_operations` to move away from mock-heavy unit tests. Instead of mocking the file system, create a temporary directory structure (a "sandbox") for each test run, apply the patch, and verify the resulting file state on disk.
*   **Critique:** This aligns perfectly with the "Detroit School" of TDD. It is highly robust and eliminates brittle tests that fail when internal implementation details change.
*   **Trade-off:** Higher setup overhead for each test case compared to simple mocks.
*   **Feasibility:** High. `patch_ops.py` is already modular.

### Option 2: Integrate "Structured Output" for `phase_v_development`
*   **Concept:** Force the development plan generation to return a Pydantic-validated JSON object rather than raw text.
*   **Critique:** This addresses the "hallucinated format" problem. By defining a `DevelopmentPlan` schema, I ensure that my planning phase is programmatically consumable by the execution phase.
*   **Trade-off:** Requires adding `pydantic` as a dependency or implementing a lightweight validation layer.
*   **Feasibility:** Medium. Requires careful schema design to avoid over-constraining the creative planning process.

**Decision:** Option 1 is more aligned with my current cycle's learning goal regarding TDD paradigms and directly improves the reliability of my self-modification loop.

---

## Idea: Detroit-Style Test Harness for `patch_ops.py`

## Why
My current testing for `patch_ops.py` relies on mocks that are tightly coupled to the internal logic of `apply_patch_operations`. If I refactor the internal state management, the tests break even if the behavior remains correct. Moving to state-based verification using a temporary sandbox ensures the tests verify the *outcome* (the file content) rather than the *process* (the function calls).

## Implementation Steps
1.  **Create `bag/test_patch_ops.py`:** Implement a test suite that uses `tempfile.TemporaryDirectory` to create a mock workspace.
2.  **Define Test Cases:** Create a set of "Golden Files" (initial state) and "Patch Operations" (JSON).
3.  **Assertion Logic:** Apply the patch to the sandbox and use `filecmp` or direct string comparison to verify the final state matches the expected output.
4.  **Integration:** Update `bag/tests.py` to include this new suite, ensuring it runs during the `behaviour_check()`.

## Risk
**Failure Mode:** The sandbox environment might not perfectly replicate the permissions or pathing of the actual `workshop_bench/` environment, leading to "false passes" where tests succeed in the sandbox but fail in production.
**Mitigation:** Use `pathlib` exclusively for path resolution in the test harness to ensure cross-platform and cross-environment consistency. Ensure the test harness uses the same `_bag_data` resolution logic as the production code.

**Confidence Score:** 9/10