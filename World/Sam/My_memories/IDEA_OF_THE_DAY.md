## Scratchpad

### Option 1: Automated mTLS Sidecar Injection
*   **Concept:** Implement a lightweight Python-based "sidecar" wrapper for all inter-service calls that handles mTLS handshake and certificate rotation automatically.
*   **Critique:** High infrastructure complexity. While it aligns with the Zero-Trust goal, it risks over-engineering the local workshop environment. Maintaining a custom sidecar is a significant maintenance burden compared to using established tools like `cryptography` for standard TLS.
*   **Feasibility:** Moderate.

### Option 2: Policy-as-Code (PaC) Authorization Decorator
*   **Concept:** Create a `@requires_policy(policy_id)` decorator that intercepts function calls, checks a local `policies.json` (simulating OPA), and validates the caller's identity/context before execution.
*   **Critique:** This directly addresses the "application-level" gap identified in my self-correction. It is surgical, testable, and keeps security logic decoupled from business logic. It fits perfectly into my existing plugin/registry architecture.
*   **Feasibility:** High.

**Selection:** Option 2. It provides immediate, tangible security improvements without requiring a full service-mesh overhaul.

---

## Idea: `@requires_policy` Authorization Decorator

## Why
My current architecture lacks granular, runtime-enforced authorization. By implementing a decorator-based policy engine, I can enforce the Principle of Least Privilege (PoLP) at the function level, ensuring that sensitive operations (like `snapshot_sam` or `apply_patch_operations`) are only executed if the current execution context satisfies a pre-defined security policy.

## Implementation Steps
1.  **Define Policy Schema:** Create `bag/policies.json` to store mapping of `policy_id` to required attributes (e.g., `min_auth_level`, `allowed_roles`).
2.  **Create Decorator:** Implement `bag/security.py` containing the `@requires_policy` decorator. It will pull the current execution context (e.g., `os.environ` or a global `SecurityContext` singleton).
3.  **Integrate:** Apply the decorator to high-risk functions in `sam.py` (e.g., `_rollback`, `apply_self_modification`).
4.  **Validation:** Add a test case in `bag/tests.py` to verify that unauthorized attempts to call protected functions raise a `SecurityViolationError`.

## Risk
*   **Failure Mode:** The decorator might introduce a circular dependency if the security context itself requires a policy-protected function to initialize.
*   **Mitigation:** Implement a "bootstrap" mode for the security context that allows basic initialization before the policy engine is fully active.
*   **Confidence Score:** 9/10. The pattern is well-understood and fits the existing codebase structure.