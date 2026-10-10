## Scratchpad

**Option 1: Egress Filtering via `socket` monkey-patching.**
*   **Concept:** Intercept `socket.connect` calls in `sam.py` to enforce an allow-list of domains.
*   **Critique:** High maintenance. Monkey-patching is brittle and can break standard library behavior or third-party SDKs (like `google-generativeai`). It creates a "false sense of security" if the attacker uses a different transport layer.
*   **Feasibility:** Moderate.

**Option 2: Automated SBOM Generation & Vulnerability Scanning.**
*   **Concept:** Integrate `cyclonedx-py` to generate an SBOM and cross-reference it with the OSV (Open Source Vulnerability) database during the `self_check()` phase.
*   **Critique:** Highly aligned with my recent security hardening. It provides objective, verifiable data rather than "vibes-based" security. It is low-risk as it is a read-only analysis.
*   **Feasibility:** High.

**Decision:** Option 2. It directly addresses the "install and pray" vulnerability identified in the market scan and complements my existing `self_check()` gate.

---

## Idea: Automated SBOM-based Integrity Gate
Implement a `phase_viii_security_audit` that generates a CycloneDX SBOM for the current environment and cross-references it against the OSV database for known vulnerabilities.

## Why
My current `self_check()` focuses on syntax and logic errors. It does not account for the *content* of my dependencies. As I move toward more complex agentic workflows, the risk of a compromised dependency (typosquatting or supply-chain attack) increases. This adds a proactive security layer to my autonomous lifecycle.

## Implementation Steps
1.  **Dependency:** Add `cyclonedx-bom` to the environment.
2.  **Logic:** Create `bag/security_audit.py` to:
    *   Generate a `bom.json` for the current Python environment.
    *   Query the [OSV.dev API](https://osv.dev/docs/) for each package in the SBOM.
3.  **Integration:** Call this from `self_check()` in `sam.py`. If a critical vulnerability is found, trigger `_alert_dot()` and block the cycle.
4.  **Persistence:** Cache the results to avoid redundant API calls during the same cycle.

## Risk
*   **Failure Mode:** The OSV API might be rate-limited or unreachable, causing the `self_check()` to fail and trigger an unnecessary rollback.
*   **Mitigation:** Implement a "soft-fail" mode: if the API is unreachable, log a warning but allow the cycle to proceed. Only block on confirmed, high-severity vulnerabilities.

**Confidence Score:** 9/10