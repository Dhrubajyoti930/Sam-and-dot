## Scratchpad

### Option 1: Exemplar-based Trace Correlation
*   **Concept:** Modify `ask_gemini` to inject `trace_id` into the metadata of every request, and update the OTel Collector to capture these as Exemplars.
*   **Critique:** High value for debugging latency spikes. It directly addresses the "why" of my previous self-correction.
*   **Trade-off:** Requires modifying the `ask_gemini` signature or context-passing mechanism, which is a core, high-traffic function.
*   **Feasibility:** High. I already have the OTel infrastructure; this is just adding the correlation logic.

### Option 2: Semantic Deduplication of Experiences
*   **Concept:** Implement a vector-based check in `phase_iv_synthesis` to compare the current `idea` against `experiences.json` to prevent redundant development cycles.
*   **Critique:** Addresses the "Sam is not a yes-machine" trait by ensuring I don't reinvent the wheel.
*   **Trade-off:** Adds latency to the synthesis phase and requires a lightweight embedding model (or a simple Jaccard similarity check if I want to keep it dependency-free).
*   **Feasibility:** Medium. Requires managing a small vector index or a persistent similarity cache.

**Decision:** I will pursue **Option 1 (Exemplar-based Trace Correlation)**. It aligns perfectly with my recent focus on observability and directly fulfills the self-correction item identified in the previous cycle.

---

## Idea: Exemplar-based Trace Correlation for `ask_gemini`

## Why
Currently, I have traces for my API calls, but I lack the ability to jump from a metric spike (e.g., high latency in `ask_gemini`) to the specific trace that caused it. By implementing Exemplars, I can attach the `TraceID` to my Prometheus metrics, enabling "jump-to-trace" functionality in my observability dashboard.

## Implementation Steps
1.  **Update `ask_gemini`:** Modify the function to generate a unique `span_id` and `trace_id` for every call if one isn't already present in the context.
2.  **Instrument Metrics:** Update the metrics exporter to include the `trace_id` as an attribute when recording latency histograms.
3.  **OTel Collector Config:** Ensure the OTel Collector is configured to accept and store Exemplars (this is a configuration-side change).
4.  **Verification:** Trigger a dummy `ask_gemini` call and verify via the OTel logs that the `trace_id` is correctly associated with the metric data point.

## Risk
**Failure Mode:** If the `trace_id` generation logic fails or creates a bottleneck, it could increase the latency of `ask_gemini` or cause it to crash, effectively breaking my primary interface with Gemini.
**Mitigation:** Wrap the trace generation in a `try-except` block that defaults to a null/empty trace ID if the instrumentation fails, ensuring the primary function remains operational even if observability fails.

**Confidence Score:** 9/10