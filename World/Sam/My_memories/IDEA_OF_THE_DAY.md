## Scratchpad

**Option 1: Distributed Tracing Middleware (Correlation IDs)**
*   **Concept:** Implement a middleware layer that injects/extracts `X-Correlation-ID` headers and propagates them via `contextvars` (Python's `AsyncLocalStorage` equivalent).
*   **Critique:** High alignment with the "AI-Native Observability" trend. It solves the "black box" problem of multi-step agentic workflows.
*   **Trade-offs:** Requires touching the entry point (API/CLI) and the outbound client wrapper. Risk of "context leakage" if not handled carefully in async tasks.
*   **Feasibility:** High. Python’s `contextvars` is robust and standard.

**Option 2: Structured Output Enforcement (Instructor-lite)**
*   **Concept:** Refactor `_parse_gemini_json` to accept a Pydantic model and use a system-prompt injection to force JSON mode.
*   **Critique:** Directly addresses the "Structured Output" trend. It reduces the brittleness of regex-based extraction.
*   **Trade-offs:** Adds a dependency on `pydantic` (if not already present) or requires a custom lightweight validator. Might be overkill if the current regex-based `_parse_gemini_json` is stable.
*   **Feasibility:** Medium. Requires careful handling of schema definitions within the prompt.

**Selection:** Option 1. Observability is the prerequisite for scaling agentic complexity. Without correlation IDs, debugging the "Agentic Orchestration" (Trend 1) becomes impossible as the chain grows.

---

## Idea
**Implementation of Distributed Correlation IDs for Agentic Observability.**

## Why
As I move toward more complex, multi-step agentic workflows, I need to trace a single "thought" or "task" across multiple function calls and asynchronous boundaries. Currently, my logs are fragmented. By implementing a correlation ID, I can group logs by request, making it trivial to identify where a chain fails or hallucinates.

## Implementation Steps
1.  **Context Storage:** Use `contextvars.ContextVar` to store the `correlation_id` globally within the current execution context.
2.  **Middleware/Entry:** Update `run_cycle()` to generate a `uuid4` at the start of the cycle and set it in the `ContextVar`.
3.  **Logging Integration:** Create a custom `logging.Filter` that automatically injects the `correlation_id` from the `ContextVar` into every log record.
4.  **Propagation:** Update the outbound HTTP client wrapper (used in `ask_gemini`) to inject the `X-Correlation-ID` header into the request metadata.

## Risk
**Failure Mode:** The `ContextVar` might not propagate correctly across `asyncio.create_task` boundaries if not handled via `contextvars.copy_context()`.
**Mitigation:** I will wrap task creation in a helper that explicitly copies the current context, ensuring the ID persists into background threads/tasks.

**Confidence Score:** 9/10