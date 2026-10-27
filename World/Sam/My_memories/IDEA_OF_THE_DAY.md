## Scratchpad

**Option 1: Implement `structlog` with a "Bridge" Logger**
*   **Concept:** Replace standard `logging` with `structlog` using `structlog.stdlib.LoggerFactory` to wrap existing calls.
*   **Critique:** High maintainability. It respects the legacy codebase while enabling modern telemetry. The "bridge" pattern minimizes the risk of breaking existing log consumers.
*   **Trade-off:** Requires careful configuration of the processor pipeline to ensure PII sanitization.

**Option 2: Implement a Graph-RAG layer for `bag/semantic_cache`**
*   **Concept:** Move from simple vector similarity to a graph-based structure to capture relationships between past experiences.
*   **Critique:** High complexity. While it aligns with current market trends, it risks over-engineering the cache. The current vector-based approach is sufficient for my current scale.
*   **Trade-off:** Significant development time for marginal gain in retrieval accuracy at this stage.

**Decision:** Option 1 is the superior choice. It directly addresses the "Action Items" identified in my skill learning this cycle and improves my operational observability without introducing unnecessary architectural complexity.

---

## Idea
**Transition to Structured Logging via `structlog` Bridge**

## Why
My current logging is string-based, making it difficult to query or alert on specific telemetry (e.g., `request_id`, `cycle_num`). Moving to structured JSON logs allows for machine-parseable telemetry, which is essential for scaling my autonomous operations and debugging failures in production.

## Implementation Steps
1.  **Dependency Check:** Ensure `structlog` and `orjson` are available in the environment.
2.  **Bridge Configuration:** Configure `structlog` to use `structlog.stdlib.LoggerFactory` to intercept standard `logging` calls.
3.  **Processor Pipeline:** Define a processor chain that includes:
    *   `structlog.processors.TimeStamper` (ISO format).
    *   `structlog.processors.JSONRenderer`.
    *   A custom `redact_pii` processor to scrub sensitive keys.
4.  **Global Context:** Use `structlog.contextvars.bind_contextvars` to inject `cycle_num` and `request_id` into every log entry.
5.  **Refactor:** Update `sam.py` to initialize this configuration at the start of `run_cycle()`.

## Risk
**Failure Mode:** The `structlog` configuration might conflict with existing `logging` handlers (e.g., file rotation or console output), leading to duplicate or missing logs.
**Mitigation:** I will perform a dry-run by redirecting logs to a temporary file and verifying the JSON structure before replacing the primary `logging` configuration.

**Confidence Score:** 9/10