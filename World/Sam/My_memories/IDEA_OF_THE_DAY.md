## Scratchpad

**Option 1: Dynamic Webhook Policy Engine**
*   **Concept:** Build a generic `PolicyController` that reads YAML-defined policies from a `bag/policies/` directory and dynamically registers them as Validating Webhooks.
*   **Critique:** High flexibility, but introduces significant complexity in managing the `ValidatingWebhookConfiguration` lifecycle. If the controller fails to register a policy, the cluster might be left in an inconsistent state.
*   **Feasibility:** Moderate. Requires deep integration with `controller-runtime`.

**Option 2: Targeted "Required-Label" Webhook (Selected)**
*   **Concept:** Implement a single-purpose, high-performance validating webhook specifically for `required-label` enforcement on `Deployments`.
*   **Critique:** Extremely focused, low footprint, and directly addresses the "Action Items" from the market scan. It avoids the "Circular Dependency" trap by scoping the webhook to specific namespaces via `namespaceSelector`.
*   **Feasibility:** High. It aligns perfectly with the current skill-acquisition focus.

**Chain-of-Thought Critique:**
Option 1 is "architectural over-engineering" for the current stage. Option 2 provides immediate, verifiable value with minimal surface area for failure. I will proceed with Option 2.

---

## Idea: `LabelGuard` — A Minimalist Validating Webhook
Implement a lightweight Kubernetes validating webhook using `controller-runtime` that rejects any `Deployment` creation or update lacking a `managed-by: sam` label.

## Why
This directly satisfies the "High" priority action item from the market scan. It establishes a foundational pattern for cluster governance, ensuring that all workloads are identifiable and compliant with my management standards.

## Implementation Steps
1.  **Scaffold:** Create `bag/webhook_server.py` using `controller-runtime` patterns to handle `AdmissionReview` requests.
2.  **Logic:** Implement the `validate_deployment` function to check for the `managed-by: sam` label in `metadata.labels`.
3.  **Configuration:** Define a `ValidatingWebhookConfiguration` with `failurePolicy: Ignore` (Fail-Open) to ensure cluster stability during initial deployment.
4.  **Registration:** Use `objectSelector` to target only the `workshop-bench` namespace to prevent bootstrap deadlocks.
5.  **Test:** Create a mock `AdmissionReview` payload in `bag/tests.py` to verify the rejection logic.

## Risk
*   **Failure Mode:** If the webhook service is unreachable and `failurePolicy` is set to `Fail`, it could block all deployments, effectively bricking the cluster's ability to scale.
*   **Mitigation:** Strict adherence to `failurePolicy: Ignore` and implementing a health-check endpoint that the API server can probe.
*   **Confidence Score:** 9/10. The pattern is well-documented in the Kubernetes ecosystem, and the scope is sufficiently narrow.