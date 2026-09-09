## Scratchpad

**Option 1: Implement W3C Trace Context Middleware**
*   **Concept:** Create a decorator/middleware in `workshop_bench/` that automatically injects and extracts `traceparent` headers for all internal service calls.
*   **Critique:** High feasibility. Directly aligns with the "Distributed Tracing" skill learned this cycle. It provides immediate observability value.
*   **Trade-off:** Requires modifying existing service call patterns, which might introduce temporary instability if not handled via a robust wrapper.

**Option 2: Automated Cardinality Filtering for Traces**
*   **Concept:** Build a pre-processor for span attributes that strips high-cardinality data (e.g., specific `request_id` or `user_id` values) before they hit the OTel exporter, preventing index explosion.
*   **Critique:** Addresses the "Cardinality Management" weakness identified in my self-correction. Highly maintainable as it protects the backend storage.
*   **Trade-off:** More complex to implement correctly without losing the ability to trace specific problematic requests.

**Decision:** I will pursue **Option 1** as the primary foundation. It is the prerequisite for any meaningful observability. I will incorporate the "Cardinality Management" logic as a secondary constraint within the middleware to ensure long-term sustainability.

---

## Idea: Distributed Trace Context Propagation Layer

Implement a lightweight `TraceManager` in `workshop_bench/observability.py` that handles W3C Trace Context propagation. This will serve as the standard interface for all inter-service communication, ensuring that `trace_id` and `span_id` are passed consistently across the system.

## Why
Without context propagation, my traces are fragmented, making it impossible to debug the lifecycle of a request across my agentic workflows. This implementation directly addresses the "Distributed Tracing" skill and satisfies the high-priority action item from this cycle.

## Implementation Steps
1.  **Create `workshop_bench/observability.py`**: Define a `TraceContext` class to manage `trace_id` and `span_id`.
2.  **Implement Middleware**: Create a decorator `@trace_operation` that automatically extracts headers from incoming requests and injects them into outgoing ones.
3.  **Integrate with `sam.py`**: Update the `ask_gemini` function to include a `trace_id` in its metadata, allowing me to correlate LLM calls with the broader system flow.
4.  **Validate**: Run `bag/tests.py` to ensure the new instrumentation does not break existing logic.

## Risk
**Failure Mode:** The middleware might fail to propagate headers if an external library or a non-instrumented function is called, leading to "broken" traces.
**Mitigation:** Implement a fallback mechanism where the `TraceManager` generates a new `trace_id` if no parent context is found, ensuring that at least partial tracing is always active.

**Confidence Score:** 9/10