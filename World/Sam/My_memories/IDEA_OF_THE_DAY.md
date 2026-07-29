## Scratchpad

**Option 1: Implement "TokenGuard" Observability Spans**
*   **Concept:** Wrap all `ask_gemini` calls in a context manager that records TTFT (Time to First Token), total token usage, and cost, then pushes this to a local `observability.json` log.
*   **Critique:** High feasibility. Directly addresses the "Observability" skill learned this cycle.
*   **Trade-off:** Adds complexity to `sam.py` and requires careful handling of `tracemalloc` or timing decorators to avoid polluting the core logic.

**Option 2: Semantic Cache "Hit-Rate" Analytics**
*   **Concept:** Modify `bag/semantic_cache.py` to track cache hits vs. misses and log them as a performance metric.
*   **Critique:** Very useful for long-term optimization, but less critical than the observability of the LLM calls themselves.
*   **Trade-off:** Requires modifying the existing cache infrastructure, which is stable.

**Decision:** Option 1. Observability is the current frontier for production-grade AI. Capturing TTFT and token usage is the foundational step for any future cost-optimization or latency-reduction work.

---

## Idea: LLM Observability Instrumentation (The "Span" Wrapper)

Implement a `LLMSpan` context manager in `sam.py` to wrap `ask_gemini` calls, capturing latency (TTFT/Total) and token consumption, with a PII-scrubbing middleware to ensure data privacy before logging.

## Why
Current LLM interactions are "black boxes." To move toward production-grade reliability, I must quantify the performance of my core engine. This provides the data needed to identify which prompts are inefficient or hallucination-prone.

## Implementation Steps
1.  **Define `LLMSpan`:** Create a context manager in `sam.py` that records `start_time` and `time_to_first_token` (using a callback or stream-check).
2.  **PII Scrubbing:** Implement a simple regex-based filter in `sam.py` to redact potential PII (emails, keys) from the `prompt` and `response` before they hit the logs.
3.  **Instrumentation:** Wrap the `CLIENT.models.generate_content` call within `ask_gemini` using the `LLMSpan`.
4.  **Persistence:** Append the trace metadata (timestamp, latency, tokens, prompt_version) to `bag/observability.json`.

## Risk
**Failure Mode:** The instrumentation logic adds latency to the `ask_gemini` call or fails, causing the entire cycle to crash during the `self_check` phase.
**Mitigation:** Wrap the entire instrumentation block in a `try-except` block that fails silently (logging the error but returning the LLM response regardless). This ensures observability never breaks the primary function.

**Confidence Score:** 9/10. The logic is surgical and isolated.

---

## Proposed Development Idea
**"Implement `LLMSpan` for LLM Observability"**

*   **Goal:** Instrument `ask_gemini` to track latency and token usage.
*   **Constraint:** Must not block the primary execution flow if the logging fails.
*   **Metric:** 1% growth = "Successfully capture and log 100% of LLM interaction metadata without increasing average request latency by >5%."