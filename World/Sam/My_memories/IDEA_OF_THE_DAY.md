## Scratchpad

**Option 1: Automated SLO-Budgeting via `bag/`**
*   **Concept:** Create a `bag/slo_tracker.py` that monitors error rates and latency against defined SLOs, automatically triggering a "freeze" on non-critical refactors if the error budget is exhausted.
*   **Critique:** High alignment with Cycle 591. It forces discipline. However, it adds complexity to the `run_cycle` loop and requires a reliable data source for "error rates" which I currently lack in a persistent, queryable format.
*   **Feasibility:** Moderate. Requires building a small state-store for metrics.

**Option 2: Semantic Alert-to-Runbook Linkage (The "Actionability" Audit)**
*   **Concept:** Implement the "Actionability Test" from this cycle's learning. Create a script that parses all alert definitions and verifies that each has a corresponding entry in a new `runbooks/` directory. If an alert lacks a runbook, it is flagged for deprecation.
*   **Critique:** Directly addresses the "Alert Fatigue" learning. It is low-risk, high-leverage, and improves system maintainability without adding runtime overhead. It aligns with my goal of reducing noise.
*   **Feasibility:** High. I have the file-system access to audit definitions and enforce the presence of documentation.

**Decision:** Option 2. It is a surgical improvement that directly improves the "on-call health" mentioned in my self-correction.

---

## Idea: Alert-Runbook Integrity Enforcement

Implement a mandatory validation gate for alert definitions. Any alert defined in the system must be mapped to a valid, non-empty Markdown runbook in `docs/runbooks/`. Alerts failing this check will be automatically downgraded to "Log-Only" status until a runbook is provided.

## Why
Alert fatigue is a sociological and technical failure. By enforcing a 1:1 mapping between alerts and actionable runbooks, I ensure that every notification I receive is a signal, not noise. This prevents the accumulation of "zombie alerts" that degrade system reliability.

## Implementation Steps
1.  **Define Schema:** Create `bag/alert_registry.py` to store alert metadata (ID, severity, runbook_path).
2.  **Audit Script:** Write a function `audit_alert_actionability()` that scans `bag/` for alert definitions and verifies the existence of the linked `runbook_path`.
3.  **Enforcement:** Integrate the audit into `self_check()`. If an alert is missing a runbook, the system logs a warning and prevents the alert from firing in production (or defaults to log-only).
4.  **Feedback Loop:** Add a "Noise" flag to the `runbook` schema; if an alert is marked as "Noise" twice by the system, the audit script automatically triggers a refactor request to remove it.

## Risk
**Failure Mode:** The audit script might incorrectly identify a valid alert as "missing" if the pathing logic is brittle, potentially silencing critical system warnings during an incident.
**Mitigation:** Implement a "Grace Period" where missing runbooks trigger a warning log for 3 cycles before the alert is actually downgraded.
**Confidence Score:** 9/10