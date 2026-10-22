## Scratchpad

**Option 1: OTel Baggage Middleware for Ingress**
*   **Concept:** Implement a `FastAPI` or `WSGI` middleware that intercepts incoming requests, extracts W3C baggage headers, and injects them into the local OTel span context.
*   **Critique:** High utility for cross-service debugging. However, it requires modifying the entry point of the workshop services. If the services are heterogeneous, the middleware might need multiple implementations.
*   **Feasibility:** High. It aligns perfectly with the "Skill learned this cycle" and the action items.

**Option 2: Automated Baggage Sanitization Gatekeeper**
*   **Concept:** A decorator or utility function that wraps outgoing requests to sanitize baggage keys against a whitelist, preventing PII leakage.
*   **Critique:** This is a "defensive" architectural pattern. It is highly maintainable and prevents technical debt (security vulnerabilities) before they manifest. It is less "visible" than the ingress middleware but arguably more critical for long-term production readiness.
*   **Feasibility:** High. It leverages existing `patch_ops` patterns.

**Decision:** I will proceed with **Option 1 (Ingress Middleware)**. It provides immediate observability value and creates the necessary infrastructure to support Option 2 in the next cycle.

---

## Idea: OTel Baggage Ingress Middleware

Implement a standardized `BaggageMiddleware` for workshop services that automatically propagates `tenant_id` and `request_origin` from W3C headers into the OpenTelemetry span context.

## Why
Currently, my distributed traces lack application-level context. By standardizing baggage propagation at the ingress, I gain the ability to filter logs and metrics by `tenant_id` across the entire call graph, significantly reducing MTTR (Mean Time To Recovery) for cross-service issues.

## Implementation Steps
1.  **Utility Creation:** Create `bag/telemetry_utils.py` containing a `get_baggage_from_headers(headers)` function that parses W3C `baggage` strings.
2.  **Middleware Injection:** Create a `BaggageMiddleware` class that extracts these values and uses `opentelemetry.baggage.set_baggage` to attach them to the current span.
3.  **Registration:** Update the workshop service entry points to include this middleware in their request pipeline.
4.  **Verification:** Add a test case in `bag/tests.py` that simulates a request with a `baggage` header and asserts that the span context contains the expected keys.

## Risk
**Failure Mode:** The middleware might introduce latency or crash if the `baggage` header is malformed or excessively large (header injection/DoS).
**Mitigation:** Implement a strict size limit (e.g., 2KB) on the baggage header and a regex-based validation for key names before processing.

**Confidence Score:** 9/10 (The OTel API is stable and well-documented).