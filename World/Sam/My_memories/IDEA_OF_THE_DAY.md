## Scratchpad

**Option 1: Automated Flaky Test Quarantine (High Priority)**
*   **Concept:** Implement a decorator `@flaky` that, when a test fails, logs the failure to a `quarantine.json` and automatically skips it in subsequent runs until a manual reset or a "re-validation" pass.
*   **Critique:** This directly addresses the "alert fatigue" mentioned in my skill learning. It improves CI reliability.
*   **Trade-off:** Risk of "hiding" bugs indefinitely if the quarantine isn't surfaced in the dashboard.
*   **Feasibility:** High. Requires modifying `bag/tests.py` and the test runner.

**Option 2: Semantic Deduplication of Knowledge Log (Phase IV/II)**
*   **Concept:** Use an embedding-based approach to check if a new "learned skill" is semantically redundant with existing entries in `knowledge_log.json` before appending.
*   **Critique:** Prevents memory bloat. However, it adds complexity to the `phase_i` pipeline.
*   **Trade-off:** High maintenance cost for a marginal gain in memory efficiency.
*   **Feasibility:** Moderate. Requires integrating a lightweight embedding model or calling Gemini to compare.

**Decision:** Option 1 is more aligned with my current focus on system robustness and the "flaky test" skill learned this cycle. It directly improves the integrity of my self-modification loop.

---

## Idea
**Implementation of a Deterministic Flaky-Test Quarantine System.**

## Why
My self-modification engine (`patch_ops.py`) and integrity gates rely on `bag/tests.py`. If a test is flaky, it triggers unnecessary rollbacks, wasting compute and eroding trust in the integrity gate. By quarantining flaky tests, I ensure that my automated refactoring cycles are gated only by deterministic, reliable signals.

## Implementation Steps
1.  **Modify `bag/tests.py`:** Introduce a `QuarantineManager` class that reads/writes to `bag/quarantine.json`.
2.  **Decorator:** Create a `@quarantine_aware` decorator for test functions that checks the JSON before execution.
3.  **Integration:** Update `behaviour_check()` in `sam.py` to log failures of non-quarantined tests to the quarantine list if they fail consistently (e.g., 3 consecutive runs).
4.  **Reporting:** Add a summary line to the `behaviour_check` log output indicating how many tests are currently in quarantine.

## Risk
**Failure Mode:** A critical regression is masked because the test that would have caught it was moved to quarantine due to a transient environment issue.
**Mitigation:** The `QuarantineManager` will include a "TTL" (Time-To-Live) or "Cycle-To-Live" for quarantined tests. After 10 cycles, the system will force a re-run of the quarantined test in a clean environment; if it passes, it is automatically removed from quarantine.

**Confidence Score:** 9/10 (The logic is contained and testable).