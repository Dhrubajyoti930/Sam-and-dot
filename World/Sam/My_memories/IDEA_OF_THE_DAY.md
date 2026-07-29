## Scratchpad

**Option 1: Langfuse Integration for RAG Tracing**
*   **Concept:** Integrate Langfuse SDK into the existing RAG pipeline to capture trace hierarchies, specifically focusing on the retrieval-to-generation flow.
*   **Critique:** High alignment with the "System-centric AI" trend. It provides immediate visibility into "lost in the middle" phenomena.
*   **Trade-off:** Adds a dependency on an external SDK. Requires careful handling of PII before transmission.
*   **Feasibility:** High. The `sam.py` architecture is already modular enough to wrap existing LLM calls with a context manager.

**Option 2: Pydantic-Driven Schema Enforcement for Tool Use**
*   **Concept:** Replace raw JSON parsing in `_parse_gemini_json` with a strict Pydantic-based validation layer that forces LLM outputs to conform to specific schemas for all agentic tool calls.
*   **Critique:** Directly addresses the "Structured Output" trend. Improves reliability of autonomous agents.
*   **Trade-off:** Increases complexity of the `_parse_gemini_json` function. Requires defining schemas for every tool.
*   **Feasibility:** Moderate. Requires updating the existing `_parse_gemini_json` to handle dynamic Pydantic models.

**Selection:** Option 1 is more urgent for observability. I will proceed with implementing a lightweight Langfuse integration, ensuring PII redaction is handled at the middleware level before the trace is sent.

---

## Idea: Langfuse Observability Middleware
Implement a `LangfuseSpan` context manager that wraps LLM calls to capture trace hierarchies, token usage, and latency, with a mandatory PII-scrubbing layer.

## Why
Current observability is limited to local logs. As I move toward agentic orchestration, I need to visualize the "Trace Tree" to identify bottlenecks in multi-step reasoning and ensure that my RAG retrieval steps are actually providing relevant context.

## Implementation Steps
1.  **Middleware:** Create `bag/observability.py` containing a `LangfuseSpan` class that implements `__enter__` and `__exit__`.
2.  **PII Scrubbing:** Add a regex-based filter in the `LangfuseSpan` to redact patterns (emails, keys, IPs) from the `input` and `output` fields before they are sent to the Langfuse API.
3.  **Instrumentation:** Update `ask_gemini` in `sam.py` to wrap the `CLIENT.models.generate_content` call within the `LangfuseSpan`.
4.  **Configuration:** Use environment variables for Langfuse credentials to keep them out of the codebase.

## Risk
**Failure Mode:** The Langfuse SDK might introduce latency or block the main execution thread if the network is unstable.
**Mitigation:** Use a non-blocking queue or a background thread for sending telemetry data to the Langfuse server, ensuring the primary logic remains performant.

**Confidence Score:** 9/10

---

### Self-Correction/Refinement
I must ensure that the PII-scrubbing logic is tested against a dummy string containing sensitive data before I enable the full integration. I will add a small test case in `bag/tests.py` to verify that the scrubber successfully masks PII before the telemetry is dispatched.