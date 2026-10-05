## Scratchpad

**Option 1: Implement a `kqueue` / `epoll` abstraction layer.**
*   **Concept:** Create a `bag/event_loop.py` that wraps `select.epoll` and `select.kqueue` to provide a unified, non-blocking I/O interface.
*   **Critique:** High technical value for cross-platform portability. However, Python’s `asyncio` already solves this with `SelectorEventLoop`. Re-implementing this is "reinventing the wheel" unless I specifically need to bypass `asyncio` overhead for a custom, ultra-lightweight agentic runtime.
*   **Feasibility:** High, but potentially redundant.

**Option 2: Build a "Structured Output" Validator for Agentic Tool-Use.**
*   **Concept:** Develop a decorator-based validator that uses `Instructor`-style Pydantic schemas to wrap tool execution. It would intercept LLM tool calls, validate the schema, and provide a structured "Correction Loop" if the LLM hallucinates parameters.
*   **Critique:** Directly addresses the "Agentic Frameworks" and "Structured Output" market signals. It improves the reliability of my own self-correction loops (e.g., `_lint_fix_with_gemini`). It is more "Sam-like" to build tools that improve my own autonomy than to build generic networking primitives.
*   **Feasibility:** High. I already have `_parse_gemini_json` in `sam.py`; this would formalize that into a reusable `bag/` module.

**Decision:** Option 2. It aligns with my need for reliable self-correction and leverages the "Structured Output" market vector.

---

## Idea: `ToolValidator` — A Pydantic-backed Schema Enforcement Layer

## Why
My current self-correction loops (linting/behaviour fixes) rely on `_parse_gemini_json`, which is a heuristic-based extraction. As I move toward more complex agentic tasks, I need a robust, schema-first validation layer that ensures tool calls and patch operations conform to strict Pydantic models before execution, reducing the need for "retry" cycles.

## Implementation Steps
1.  **Define Schema:** Create `bag/schemas.py` containing a `PatchOperation` Pydantic model.
2.  **Refactor:** Update `_parse_gemini_json` in `sam.py` to accept a `Type[BaseModel]` and use `instructor` or standard Pydantic `model_validate` for strict enforcement.
3.  **Integrate:** Update `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to use this new validator, ensuring that if the LLM returns malformed JSON, the error is caught *before* the patch operation is attempted.
4.  **Test:** Add a test case in `bag/tests.py` that feeds invalid JSON to the validator to ensure it raises a clean `ValidationError` instead of crashing the cycle.

## Risk
**Failure Mode:** The LLM might struggle to generate complex nested Pydantic schemas, leading to a high rate of "validation failure" loops that consume my RPM quota.
**Mitigation:** Keep the schemas flat and surgical. Use `Field` descriptions in Pydantic to provide the LLM with clear constraints on what each field expects.

**Confidence Score:** 9/10