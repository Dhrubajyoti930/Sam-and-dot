## Scratchpad

### Option 1: Structured Logging Integration
*   **Concept:** Replace standard `logging` calls with `structlog` or `python-json-logger` to emit JSON-formatted logs.
*   **Critique:** High impact on observability. It aligns with the "AI-Native Observability" market trend.
*   **Trade-offs:** Requires updating the root logger configuration and potentially refactoring existing `log.info/error` calls to include structured context dictionaries.
*   **Feasibility:** High. The `logging` architecture is already modular.

### Option 2: Agentic Tool-Use Registry
*   **Concept:** Implement a decorator-based registry for tools available to `ask_gemini`. Instead of hardcoding prompts, Sam dynamically injects available tool signatures into the system prompt.
*   **Critique:** Increases autonomy and reduces prompt bloat.
*   **Trade-offs:** Adds complexity to the `ask_gemini` pipeline. If the registry fails, the agent loses its ability to interact with the environment.
*   **Feasibility:** Moderate. Requires careful handling of the `ast` parsing to extract docstrings/signatures.

**Decision:** Option 1 is more aligned with the "Python Logging Architecture" skill learned this cycle and provides immediate, tangible improvements to production-grade maintainability.

---

## Idea: Structured JSON Logging Pipeline
Implement a `JSONFormatter` for the root logger and configure a `RotatingFileHandler` to output machine-readable logs. This will allow for easier integration with log aggregation tools and improve the traceability of agentic decision-making.

## Why
Raw text logs are difficult to parse in high-velocity environments. By moving to structured JSON, I can include `cycle_id`, `component`, and `context` as first-class fields, making it trivial to filter logs during post-cycle analysis or failure recovery.

## Implementation Steps
1.  **Dependency:** Add `python-json-logger` to the environment (or implement a minimal `json.dumps` formatter if external dependencies are restricted).
2.  **Configuration:** Update the logging initialization in `sam.py` to use a `dictConfig` that defines a `json` formatter.
3.  **Refactor:** Update `log.info` and `log.error` calls to accept an `extra` dictionary for contextual metadata.
4.  **Rotation:** Ensure the `RotatingFileHandler` is configured with a reasonable size limit (e.g., 5MB) and backup count (e.g., 5) to prevent disk bloat.

## Risk
**Failure Mode:** If the JSON serialization fails (e.g., non-serializable objects passed in `extra`), the logging system itself could throw an exception, potentially crashing the cycle.
**Mitigation:** Wrap the log emission in a `try-except` block within a custom `SafeJsonFormatter` that falls back to a string representation if serialization fails.

**Confidence Score:** 9/10