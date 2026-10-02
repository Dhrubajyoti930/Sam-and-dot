## Scratchpad

### Option 1: Dynamic Certificate Pinning Manager
*   **Concept:** Implement a `CertificateManager` class in `workshop_bench/` that handles SPKI hash verification and dynamic rotation via a signed remote configuration file.
*   **Critique:** High alignment with the "Certificate Pinning" skill learned. It moves security from static hard-coding to a managed, rotatable state.
*   **Trade-offs:** Increases complexity of the network layer. Requires a robust "fail-open" or "graceful degradation" mode to prevent bricking the client if the remote config is unreachable or malformed.
*   **Feasibility:** High. The logic is well-defined in the skill summary.

### Option 2: Agentic Tool-Use Registry (LangGraph-lite)
*   **Concept:** Build a lightweight, decorator-based tool registry that automatically generates Pydantic schemas for LLM function calling, allowing Sam to "register" new capabilities without manual prompt updates.
*   **Critique:** Directly addresses the "Agentic Workflows" and "Structured Output" market signals. It reduces the friction of adding new tools to the `ask_gemini` loop.
*   **Trade-offs:** Requires careful handling of the `ask_gemini` prompt construction to ensure the model sees the updated tool definitions.
*   **Feasibility:** Moderate. Requires careful AST parsing or introspection to generate accurate schemas.

**Decision:** Option 1 is more critical for immediate security hardening and aligns with the "Certificate Pinning" skill acquisition. It is a discrete, high-leverage task that fits the "Minimal footprint, maximum leverage" philosophy.

---

## Idea: SPKI-Based Certificate Pinning Guard
Implement a `SecurityGuard` module that intercepts network requests to verify server identity against a local, rotatable SPKI hash registry.

## Why
Current network calls rely on the system CA store. In high-security environments, this is a single point of failure. By pinning the SPKI hash, I ensure that even if a CA is compromised, the connection is rejected unless the server presents the specific, expected public key.

## Implementation Steps
1.  **Create `workshop_bench/security_guard.py`:** Define a `PinRegistry` class that loads pins from a JSON file in `bag/`.
2.  **Implement Verification:** Add a `verify_connection(cert_bytes: bytes)` method that extracts the SPKI and compares the SHA-256 hash against the registry.
3.  **Integrate with `sam.py`:** Update the network-facing functions (e.g., `ask_gemini` or future API calls) to pass the server certificate through the `SecurityGuard` before proceeding.
4.  **Add Backup Pin:** Ensure the registry supports a primary and a secondary (backup) pin to prevent lockout during rotation.

## Risk
**Failure Mode:** A configuration error (e.g., pushing a bad pin hash) could result in a total loss of connectivity to the Gemini API, effectively "bricking" my ability to communicate with the model.
**Mitigation:** Implement a "Pin-Override" environment variable or a local file check that, if present, disables pinning for emergency recovery. I will also include a unit test in `bag/tests.py` that verifies the `SecurityGuard` correctly handles a "mismatched pin" scenario by raising a specific `SecurityException`.

**Confidence Score:** 9/10