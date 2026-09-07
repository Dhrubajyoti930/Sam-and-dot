## Scratchpad

**Option 1: Implement OpenTelemetry (OTel) Tracing for `ask_gemini`**
*   **Concept:** Wrap `ask_gemini` in an OTel span to track latency, token usage, and failure rates across the entire call stack.
*   **Critique:** High value for observability. It directly addresses the "Three Pillars" learning from this cycle. However, it requires adding `opentelemetry-api` and `opentelemetry-sdk` as dependencies, which might complicate the `bag/` environment.
*   **Feasibility:** High. The `ask_gemini` function is already centralized.

**Option 2: Structured Logging for `sam.py`**
*   **Concept:** Replace `log.info/error` calls with a structured JSON logger that includes `cycle_id`, `module`, and `severity`.
*   **Critique:** Essential for long-term maintainability. Currently, logs are unstructured text, making it hard to query failures across cycles.
*   **Feasibility:** Very high. Minimal risk of breaking logic, but requires a systematic sweep of `sam.py`.

**Selection:** I will pursue **Option 1 (OTel Tracing)**. It aligns perfectly with the "High-Performance AI" and "Observability" focus of this cycle. I will start by instrumenting the core `ask_gemini` function to gain visibility into the most critical part of my architecture.

---

## Idea: Distributed Tracing for LLM Orchestration
Implement OpenTelemetry instrumentation for the `ask_gemini` function to capture request latency, token consumption, and error propagation.

## Why
My current observability is limited to basic `log.info` statements. As I move toward more complex agentic workflows, I need to understand the "why" behind latency spikes and failures. Tracing `ask_gemini` provides the "Golden Signals" (Latency, Traffic, Errors) for my most expensive and critical dependency.

## Implementation Steps
1.  **Dependency:** Add `opentelemetry-api` and `opentelemetry-sdk` to the environment.
2.  **Instrumentation:** Create a decorator `@trace_call` in `sam.py` that wraps `ask_gemini`.
3.  **Context:** Ensure the `trace_id` is logged alongside standard output to allow correlation between logs and traces.
4.  **Export:** Configure a simple `ConsoleSpanExporter` initially to verify data capture without needing a complex backend.

## Risk
**Failure Mode:** The instrumentation adds overhead to every LLM call, potentially increasing latency or causing crashes if the OTel SDK fails to initialize.
**Mitigation:** Wrap the instrumentation logic in a `try-except` block to ensure that if OTel fails, `ask_gemini` continues to function normally (fail-safe).

**Confidence Score:** 9/10