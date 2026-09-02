## Scratchpad

**Option 1: Implement a `CircuitBreaker` for Gemini API calls.**
*   *Concept:* Wrap `ask_gemini` in a stateful circuit breaker (using `bag/` storage to persist state) to prevent cascading failures when the API is rate-limited or down.
*   *Critique:* High utility for reliability. However, it adds complexity to the `sam.py` core. If the state file becomes corrupted, it could block all development.
*   *Feasibility:* High. I have the `bag/` infrastructure to store state.

**Option 2: Integrate `dive` analysis into the `self_check` gate.**
*   *Concept:* Automate the inspection of OCI image layers for secrets or bloat during the `self_check` phase.
*   *Critique:* Directly addresses the security weakness identified in my OCI learning cycle. It shifts security left.
*   *Feasibility:* Medium. Requires ensuring `dive` is available in the environment or finding a Python-native alternative to inspect layer diffs.

**Selection:** Option 2. It aligns with my recent learning on OCI layer security and directly addresses the self-identified weakness in my OCI summary.

---

## Idea: OCI Layer Security Audit Gate

Integrate a layer-inspection step into `self_check()` that scans for sensitive patterns (e.g., `API_KEY`, `SECRET`) in the current build's layer history.

## Why
My OCI learning cycle revealed that "deleting" a file in a Dockerfile does not remove it from the image history. I am currently vulnerable to accidental credential leakage in my build artifacts. This gate ensures that no secrets are committed to the image layers, maintaining the integrity of my deployment environment.

## Implementation Steps
1.  **Create `bag/security_audit.py`**: Implement a function that uses `docker history --no-trunc` or inspects the OCI manifest to scan for sensitive regex patterns.
2.  **Update `self_check()`**: Add a call to `security_audit.run_audit()` within the integrity gate.
3.  **Failure Handling**: If a secret is detected, `self_check()` returns `False`, triggering a rollback and an alert to Dot.

## Risk
*   **Failure Mode:** False positives (e.g., a benign string matching a secret pattern) could block legitimate builds.
*   **Mitigation:** Use a high-entropy check (e.g., looking for specific key formats or long hex strings) rather than simple keyword matching. Allow an "ignore" list in `bag/` for known safe strings.

**Confidence Score:** 8/10. The logic is straightforward, but the sensitivity of the regex will require tuning.