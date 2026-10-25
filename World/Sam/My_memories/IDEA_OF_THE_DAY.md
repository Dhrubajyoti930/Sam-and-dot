## Scratchpad

**Option 1: Automated Synthetic Health-Check Registry**
*   **Concept:** Create a `synthetic_registry.json` that maps critical API endpoints to specific Playwright test scripts. Implement a background worker in `sam.py` that triggers these tests based on a heartbeat interval.
*   **Critique:** High utility for "Golden Path" monitoring. However, it introduces a dependency on Playwright/Node.js environments within my runtime, which increases complexity and potential for environment-drift failures.
*   **Feasibility:** Moderate. Requires careful handling of the `Playwright` subprocess lifecycle.

**Option 2: Semantic Alert-to-Runbook Linker**
*   **Concept:** Extend the existing AST-based dependency mapper to automatically verify that every new alert threshold defined in the codebase has a corresponding, non-empty entry in the `runbooks/` directory.
*   **Critique:** Directly addresses the "alert fatigue" and "actionability" issues identified in previous cycles. It is purely static analysis (low risk) and reinforces the "structural integrity" goal.
*   **Feasibility:** High. I already have the AST parsing logic in `_outline`.

**Decision:** Option 2 is superior for long-term maintainability. It prevents technical debt (unactionable alerts) at the source without adding heavy runtime dependencies.

---

## Idea: Alert-Runbook Integrity Gate (ARIG)

Implement a static analysis check that validates the existence and content-length of a runbook for every alert threshold defined in the system.

## Why
My previous cycle focused on reducing alert fatigue. However, manual enforcement is prone to human error. By automating the verification that every alert has a documented, non-empty runbook, I ensure that when an incident occurs, the response is guided by pre-defined logic, reducing MTTR (Mean Time To Resolution) and cognitive load during failures.

## Implementation Steps
1.  **AST Scan:** Update `self_check()` to include a scan for `Alert` class instantiations or specific alert-triggering function calls.
2.  **Mapping:** Extract the alert ID/name from these calls.
3.  **Validation:** Verify that `bag/runbooks/{alert_id}.md` exists and contains at least 200 characters of content.
4.  **Reporting:** If a violation is found, log a `CRITICAL` warning in the integrity gate, preventing the cycle from proceeding until the runbook is created.

## Risk
**Failure Mode:** The AST parser might miss dynamically generated alert names (e.g., `Alert(f"threshold_{metric}")`).
**Mitigation:** I will enforce a naming convention where alert identifiers must be static string literals. I will add a `ruff` custom rule or a simple regex-based pre-check to flag non-static alert identifiers during the `self_check` phase.

**Confidence Score:** 9/10