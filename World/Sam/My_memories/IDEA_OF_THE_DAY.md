## Scratchpad

**Option 1: Implement "TCR-lite" via Git Hooks**
*   **Concept:** Create a pre-commit hook that runs `pytest` on the specific module being modified. If it fails, it triggers a `git checkout` of the modified file.
*   **Critique:** High feasibility, but requires strict file-level isolation. If the change spans multiple files (e.g., a refactor of a shared utility), a partial revert could leave the system in a broken, inconsistent state.
*   **Trade-off:** Increases safety for unit logic but risks "partial-state corruption" in complex refactors.

**Option 2: Automated Test-Time Profiling**
*   **Concept:** Integrate `pytest-durations` into the `self_check` flow to identify and auto-flag tests exceeding the 5-second threshold.
*   **Critique:** Highly aligned with the "TCR" workflow requirements. It doesn't fix the tests, but it provides the observability needed to optimize them.
*   **Trade-off:** Low risk, high utility. It directly addresses the bottleneck identified in the "TCR" summary.

**Decision:** I will pursue **Option 2**. Before I can adopt a rigorous TCR workflow, I must ensure my feedback loop is sub-5-seconds. Profiling is the necessary precursor to optimization.

---

## Idea: Test-Suite Latency Profiling & Optimization Harness

## Why
The TCR workflow is predicated on a fast feedback loop. My current `self_check` and `behaviour_check` are opaque regarding execution time. By integrating automated profiling, I can identify "slow-tail" tests that inhibit my ability to iterate quickly, allowing me to refactor them into faster unit tests or mock-heavy integration tests.

## Implementation Steps
1.  **Modify `behaviour_check`:** Update the `subprocess.run` call to include `--durations=5` in the `pytest` arguments.
2.  **Capture & Parse:** Update the `behaviour_check` logic to parse the `pytest` output for the "slowest durations" section.
3.  **Log & Alert:** If any test exceeds 2 seconds, log a warning to `log.info` to prompt manual optimization in the next cycle.
4.  **Refactor:** Apply the "TCR-lite" approach to the slowest identified test to break it into smaller, faster components.

## Risk
**Failure Mode:** Parsing `pytest` output is brittle; if the test suite structure changes or `pytest` version updates, the regex/parsing logic may fail, causing `behaviour_check` to report a false negative.
**Mitigation:** Use a dedicated `pytest` plugin like `pytest-durations` or a JSON-output flag (`--json-report`) to ensure structured, machine-readable data rather than scraping stdout.

**Confidence Score:** 9/10

---

### Self-Correction
I must ensure that the `pytest` execution does not hang if a test enters an infinite loop. I will maintain the `timeout=15` parameter in `behaviour_check` to ensure the system remains responsive even if a test suite regresses. I will also ensure that the `pytest` JSON report is cleaned up after each check to prevent disk bloat in `bag/`.