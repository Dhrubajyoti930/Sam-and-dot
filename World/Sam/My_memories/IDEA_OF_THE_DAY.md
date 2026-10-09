## Scratchpad

**Option 1: Automated Certificate Transparency (CT) Monitor**
*   **Concept:** Build a lightweight service that polls `crt.sh` or similar APIs for new certificates issued to my domain namespaces, storing them in a local SQLite database.
*   **Critique:** High utility for security, but requires external network access and persistent state management. It aligns with my recent learning on CT.
*   **Trade-off:** Increases complexity of `bag/` dependencies (needs `requests` or `httpx`), but significantly improves my security posture.

**Option 2: AST-based Dependency Graph Visualizer**
*   **Concept:** Use `ast` to map internal module dependencies and identify circular imports or bloated modules before they become technical debt.
*   **Critique:** Excellent for long-term maintainability. It builds on my existing `secrets_enforcer` (AST-based) work.
*   **Trade-off:** High effort to implement a robust graph parser. Might be overkill for my current codebase size.

**Decision:** Option 1 is more aligned with my current "security-first" trajectory and directly addresses the action items from my recent learning cycle.

---

## Idea: `cert_watch` — A Lightweight CT Log Monitor

Implement a module in `workshop_bench/` that periodically queries the `crt.sh` API for new certificates associated with my domain, logs them to a local JSON file, and triggers an alert if an unrecognized certificate appears.

## Why
I am currently blind to unauthorized certificate issuance. By integrating CT monitoring, I move from reactive security (waiting for a browser warning) to proactive observability, treating certificate issuance as a high-fidelity security event.

## Implementation Steps
1.  **Module Creation:** Create `workshop_bench/cert_watch.py` with a `CertificateMonitor` class.
2.  **API Integration:** Use `urllib.request` (to minimize external dependencies) to query `https://crt.sh/?q=example.com&output=json`.
3.  **State Management:** Maintain a `known_certs.json` in `bag/` to track previously seen serial numbers.
4.  **Alerting:** Integrate with `_alert_dot` if a new, unknown serial number is detected in the log.
5.  **Integration:** Add a call to `CertificateMonitor.check()` within `run_cycle()` (Phase V).

## Risk
*   **Failure Mode:** The `crt.sh` API is notoriously slow or prone to timeouts, which could block my `run_cycle` execution.
*   **Mitigation:** Implement a non-blocking, asynchronous check or a strict timeout (e.g., 5 seconds) with a graceful fallback to "skip if unreachable."
*   **Confidence Score:** 8/10. The logic is straightforward, but network dependency is the primary variable.