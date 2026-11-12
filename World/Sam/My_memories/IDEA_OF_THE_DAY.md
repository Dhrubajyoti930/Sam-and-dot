## Scratchpad

### Option 1: Automated Dependency Health Monitor
*   **Concept:** Implement a script that parses `requirements.txt` and queries the PyPI API (or a local cache) to identify outdated packages and known CVEs.
*   **Critique:** High utility for long-term stability. However, it risks "dependency churn" if not gated by a robust test suite. It aligns with the "Dependency Upgrade Radar" skill learned this cycle.
*   **Feasibility:** High. Python’s `packaging` library and `requests` make this straightforward.

### Option 2: AST-Based "Impact Analysis" for Patches
*   **Concept:** Before applying a patch, use `ast` to map which functions are modified and cross-reference them with `bag/tests.py` to identify which tests *must* pass to ensure safety.
*   **Critique:** This significantly hardens the `apply_patch_operations` logic. It moves from "run all tests" to "targeted verification." It is more complex to implement but provides higher long-term safety.
*   **Feasibility:** Moderate. Requires robust AST traversal.

**Decision:** Option 1 is more aligned with the immediate "Action Items" identified in the skill-learning phase. I will implement a lightweight SCA (Software Composition Analysis) tool to audit dependencies.

---

## Idea: `bag/audit_deps.py` — Automated Dependency Vulnerability Scanner

### Why
My current architecture lacks visibility into the security posture of my dependencies. As I integrate more agentic frameworks (like LangGraph), the risk of supply-chain vulnerabilities increases. This tool provides the "SCA" capability requested in my action items.

### Implementation Steps
1.  **Create `bag/audit_deps.py`**: A script that reads `requirements.txt`.
2.  **Integration**: Use `pip-audit` (if available) or a direct query to the [OSV.dev API](https://osv.dev/) to check for vulnerabilities.
3.  **Reporting**: Log findings to `log/audit.log`. If high-severity CVEs are found, trigger `_alert_dot` to notify the owner.
4.  **CI Hook**: Update `self_check()` in `sam.py` to optionally run this audit during the integrity gate.

### Risk
*   **Failure Mode:** The API call to OSV.dev might fail or time out, causing the `self_check` to hang or crash.
*   **Mitigation:** Wrap the audit in a `try-except` block with a strict 5-second timeout. If it fails, log a warning but do not block the cycle (fail-open).

**Confidence Score:** 9/10

---

## Proposed Development Idea

### ## Idea
Implement `bag/audit_deps.py` to perform automated Software Composition Analysis (SCA) against the OSV.dev API.

### ## Why
To satisfy the "Dependency Upgrade Radar" action item: "Integrate an automated SCA tool into the CI pipeline to block builds with high-severity CVEs."

### ## Implementation Steps
1.  **Develop `bag/audit_deps.py`**:
    *   Parse `requirements.txt` to extract package names and versions.
    *   Construct POST requests to `https://api.osv.dev/v1/query`.
    *   Filter results for `severity: CRITICAL` or `HIGH`.
2.  **Update `sam.py`**:
    *   Add `run_security_audit()` to `self_check()`.
    *   If vulnerabilities are found, call `_alert_dot()` with the CVE details.
3.  **Test**: Run the audit against a known vulnerable version of a common package to verify detection.

### ## Risk
*   **Failure Mode:** Network instability during the API call.
*   **Mitigation:** Implement a non-blocking execution path; if the audit service is unreachable, log the error and proceed with the cycle to maintain availability.