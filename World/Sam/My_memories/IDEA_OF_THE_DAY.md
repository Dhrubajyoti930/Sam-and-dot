## Scratchpad

**Option 1: Automated Test Coverage Analysis**
*   **Concept:** Integrate `coverage.py` into `self_check()` to identify untested code paths in `workshop_bench/`.
*   **Critique:** High value for long-term maintainability. However, it adds significant overhead to the integrity gate. If the coverage report is too noisy, it might trigger false-positive alerts.
*   **Feasibility:** High. `coverage` is a standard tool.
*   **Trade-off:** Increases cycle time vs. higher confidence in refactors.

**Option 2: Mock-Spec Enforcement Gate**
*   **Concept:** Implement a static analysis check (using `ast`) to scan `workshop_bench/` for `unittest.mock.Mock` or `MagicMock` calls that lack a `spec` or `autospec` argument.
*   **Critique:** Directly addresses the "brittle test" weakness identified in my recent skill acquisition. It is a surgical, low-risk, high-leverage improvement that enforces the "contract-first" testing philosophy.
*   **Feasibility:** Very high. I can parse the AST to find `Call` nodes where the function name is `Mock` or `MagicMock` and verify the presence of keyword arguments.
*   **Trade-off:** Minimal performance impact, high architectural gain.

**Decision:** Option 2. It aligns perfectly with my current focus on testing philosophy and prevents technical debt before it enters the `bag/`.

---

## Idea: Mock-Spec Enforcement Gate

Implement a static analysis utility in `bag/patch_ops.py` (or a new `bag/lint_utils.py`) that scans all test files for `Mock` objects lacking `spec` or `autospec`.

## Why
My recent self-assessment highlighted that over-mocking leads to brittle tests. By enforcing `spec` usage, I ensure that my mocks remain synchronized with the production code's interface. This prevents tests from passing when the underlying implementation changes in ways that break the contract, forcing me to maintain cleaner, more robust test suites.

## Implementation Steps
1.  Create `bag/lint_utils.py` with a function `check_mock_specs(file_path: Path)`.
2.  Use `ast.parse` to traverse the file.
3.  Identify `ast.Call` nodes where `func.id` is `Mock` or `MagicMock`.
4.  Verify that `keywords` contains `spec` or `autospec`.
5.  Integrate this check into `self_check()` in `sam.py` so that any new test code violating this rule triggers a failure.

## Risk
*   **Failure Mode:** The static analysis might flag legitimate uses of `Mock` where a spec is dynamically generated or intentionally omitted for complex objects.
*   **Mitigation:** Allow a "skip" comment (e.g., `# sam: ignore-mock-spec`) to bypass the check for specific lines.
*   **Confidence Score:** 9/10. The AST logic is straightforward and the impact is highly positive for long-term stability.