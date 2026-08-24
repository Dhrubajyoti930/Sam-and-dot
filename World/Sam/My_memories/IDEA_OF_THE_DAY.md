## Scratchpad

**Option 1: Locust-based Performance Regression Suite**
*   **Concept:** Integrate the learned Locust skills into the CI pipeline to automatically baseline API latency.
*   **Critique:** High value for stability. However, it requires setting up a mock server environment or a stable staging endpoint, which might be outside the current `sam.py` scope.
*   **Feasibility:** Moderate. Requires careful handling of environment variables and test data isolation.

**Option 2: Agentic "Self-Healing" Loop for Failed Tests**
*   **Concept:** Enhance `behaviour_check()` to not just alert Dot, but to automatically attempt a "surgical repair" using the `_behaviour_fix_with_gemini` logic before escalating to a full rollback.
*   **Critique:** This aligns with the "Agentic Workflows" market signal. It reduces downtime but risks "infinite loop" scenarios if the LLM keeps proposing the same broken patch.
*   **Feasibility:** High. The infrastructure for `_behaviour_fix_with_gemini` already exists; it just needs to be integrated into the `behaviour_check` flow.

**Decision:** Option 2. It directly addresses the "Agentic Workflows" market signal and improves my autonomy by reducing the frequency of manual interventions required by Dot.

---

## Idea: Autonomous Behavioural Self-Healing

Implement an automated "Retry-with-Context" loop within `behaviour_check()`. If a test fails, Sam will perform one automated attempt to fix the regression by feeding the test failure and the recent git-diff (or patch history) to Gemini, applying the fix, and re-running the test *before* triggering a rollback.

## Why
The current `behaviour_check` is binary: it fails and rolls back. By adding a "Self-Healing" layer, I can resolve minor, non-critical regressions (like import errors or logic typos) autonomously, keeping the development velocity high while maintaining system integrity.

## Implementation Steps
1.  **Modify `behaviour_check()`:** Update the failure branch to call `_behaviour_fix_with_gemini` if a `retry_count` (stored in a temporary file) is less than 1.
2.  **State Persistence:** Create a temporary `bag/retry_state.json` to track the number of attempts to prevent infinite loops.
3.  **Verification:** If the second attempt passes, log the success and clear the retry state. If it fails again, proceed to the existing `_alert_dot` and `_rollback` logic.

## Risk
**Failure Mode:** The LLM might hallucinate a "fix" that passes the specific test but introduces a subtle logic bug elsewhere in the system.
**Mitigation:** The `_behaviour_fix_with_gemini` will be restricted to the files identified in the test failure stack trace, and the `self_check()` (Ruff) will run immediately after the patch to ensure no syntax errors were introduced.

**Confidence Score:** 8/10