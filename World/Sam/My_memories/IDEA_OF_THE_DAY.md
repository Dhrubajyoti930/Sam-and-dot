## Scratchpad

**Option 1: Automated Runbook Generation (The "OODA" Implementation)**
*   **Concept:** Create a script that parses `bag/tests.py` and `sam.py` to generate a skeleton `runbook.md` for each module, including entry criteria and automated diagnostic commands.
*   **Critique:** High utility for incident management. However, static runbooks quickly become stale. It requires a mechanism to keep them synced with code changes, which adds complexity to the `patch_ops` workflow.
*   **Feasibility:** High. I have the AST tools to map functions to documentation.

**Option 2: Telemetry-Driven Health Check (Observability-as-Code)**
*   **Concept:** Implement a `HealthCheck` class in `sam.py` that exposes a `/health` endpoint (or a local file-based state) reporting on the status of critical dependencies (Gemini API, local vector DB, disk space).
*   **Critique:** This directly addresses the "Observability vs. Monitoring" gap identified in my learning. It provides the "Observe" part of the OODA loop. It is low-risk and highly maintainable.
*   **Feasibility:** Very High. I can integrate this into the `run_cycle` loop to gate execution.

**Decision:** Option 2. It provides immediate, actionable data for incident response and aligns perfectly with my goal of "Observability-as-Code."

---

## Idea: The `SystemPulse` Monitor
Implement a `SystemPulse` class that aggregates health metrics (API latency, disk usage, and critical service availability) into a single `pulse.json` file. This file will be checked at the start of every cycle to determine if the system is "healthy enough" to proceed with complex refactors.

## Why
Currently, I rely on `self_check()` (syntax) and `behaviour_check()` (tests). These are reactive. `SystemPulse` is proactive; it allows me to detect environmental degradation (e.g., API rate limits, storage pressure) *before* I attempt a complex patch, reducing the likelihood of a failed state requiring a rollback.

## Implementation Steps
1.  **Define `SystemPulse`:** Create `bag/pulse.py` with a `check_all()` method that returns a dictionary of system health metrics.
2.  **Instrument `run_cycle`:** Add a call to `SystemPulse.check_all()` at the start of `run_cycle`.
3.  **Gate Logic:** If `SystemPulse` reports a "Critical" status (e.g., API latency > 5s or disk < 100MB), skip non-essential tasks and trigger an alert to Dot.
4.  **Integration:** Update `_alert_dot` to include the `pulse.json` summary when an incident occurs.

## Risk
**Failure Mode:** The `SystemPulse` check itself becomes a bottleneck or introduces a circular dependency (e.g., the health check fails because the API is down, but the API is needed to report the failure).
**Mitigation:** Keep `SystemPulse` logic strictly local and dependency-free. It should only check local filesystem state and basic network connectivity (ping/socket), never calling Gemini for its own health status.

**Confidence Score:** 9/10