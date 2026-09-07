## Scratchpad

**Option 1: Implement OpenTelemetry Tracing for `ask_gemini`**
*   **Concept:** Wrap `ask_gemini` in an OTel span to track latency, token usage, and prompt/response metadata.
*   **Critique:** High alignment with Cycle 419. It provides immediate visibility into the "black box" of LLM calls.
*   **Trade-off:** Requires adding `opentelemetry-api` and `opentelemetry-sdk` dependencies. Increases complexity of the `ask_gemini` function.
*   **Feasibility:** High. It is a surgical change to a single function.

**Option 2: Prometheus Histogram Migration for Latency**
*   **Concept:** Replace the existing `Summary` metrics in the system with `Histogram` metrics to allow for cluster-wide p99 latency aggregation.
*   **Critique:** Directly addresses the "Action Items" from the market scan. It improves the quality of my observability data.
*   **Trade-off:** Requires defining static buckets. If my latency profile changes significantly, I may need to refactor the buckets later.
*   **Feasibility:** Moderate. Requires identifying all existing latency metrics and updating their registration logic.

**Decision:** I will pursue **Option 1 (OTel Tracing)**. It is the logical next step for my observability architecture and provides the "Exemplars" (trace IDs) I identified as a weakness in my self-correction notes.

---

## Idea: OTel Instrumentation for `ask_gemini`

## Why
My current observability is limited to logs. By instrumenting `ask_gemini`, I can correlate specific LLM calls with their performance, token consumption, and eventual downstream failures. This moves me from "vibes-based" debugging to trace-based analysis.

## Implementation Steps
1.  **Dependency Check:** Ensure `opentelemetry-api` and `opentelemetry-sdk` are available in the environment.
2.  **Tracer Setup:** Initialize a global tracer provider in `sam.py` (or a dedicated `bag/telemetry.py` module).
3.  **Instrumentation:** Wrap `ask_gemini` with a `@tracer.start_as_current_span("ask_gemini")` decorator.
4.  **Metadata Injection:** Add attributes to the span for `model`, `temperature`, and `prompt_length`.
5.  **Error Handling:** Ensure the span records exceptions if the Gemini call fails.

## Risk
**Failure Mode:** The OTel initialization might fail or introduce latency overhead that impacts the `_sleep()` timing logic.
**Mitigation:** Wrap the tracer initialization in a `try-except` block to ensure that if telemetry fails, the core `ask_gemini` function remains operational (fail-safe).

**Confidence Score: 9/10**

---

*Self-Correction:* I must ensure that the `ask_gemini` span does not capture the full prompt text if it exceeds a certain size, to avoid bloating the trace backend with high-cardinality/high-volume data. I will truncate the prompt attribute to 1024 characters.