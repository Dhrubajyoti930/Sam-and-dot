## Scratchpad

**Option 1: `beartype` Integration for Data Ingestion**
*   **Concept:** Apply `@beartype` to the `_parse_gemini_json` and `ask_gemini` return-handling logic to enforce strict runtime type checking on incoming LLM data.
*   **Critique:** High feasibility. It directly addresses the "spooky action" of malformed JSON propagating through the system. It aligns with my recent learning.
*   **Trade-off:** Minimal performance overhead, but requires careful handling of `Annotated` types for complex nested JSON structures.

**Option 2: GraphRAG-lite for Memory Retrieval**
*   **Concept:** Implement a simple adjacency list in `bag/` to track relationships between `knowledge_log.json` entries, moving beyond simple list-based retrieval.
*   **Critique:** High complexity. Might be overkill for my current scale. It risks "feature creep" when I should be focusing on hardening the existing runtime.
*   **Trade-off:** Significant architectural gain in "memory" quality, but high risk of introducing bugs in the `phase_ii` logic.

**Selection:** Option 1. It is a surgical, high-leverage refactor that directly improves system integrity without bloating the codebase.

---

## Idea: Runtime Type Enforcement for LLM Boundaries

Implement `beartype` decorators on the primary data-ingestion entry points (`_parse_gemini_json` and `ask_gemini` return handlers) to ensure that the data flowing from Gemini into my internal state machines strictly adheres to expected schemas.

## Why
My current system relies on `Pydantic` for schema validation, but `beartype` provides a faster, decorator-based runtime check that catches type mismatches at the call site. By enforcing types at the boundary where external data enters, I prevent invalid types from ever reaching the core logic, reducing the need for defensive `isinstance` checks throughout the codebase.

## Implementation Steps
1.  **Dependency Check:** Ensure `beartype` is available in the environment.
2.  **Decorator Application:** Apply `@beartype` to `_parse_gemini_json(text: str, schema=None) -> dict | list | None`.
3.  **Refinement:** Use `typing.Annotated` with `beartype.vale.Is` to validate that the returned dictionary contains required keys (e.g., `filename`, `operation`) before it hits the patch-op logic.
4.  **Verification:** Run `bag/tests.py` to ensure the runtime checks do not interfere with existing valid data flows.

## Risk
**Failure Mode:** `beartype` might raise a `BeartypeCallHintParamViolation` if the LLM returns a slightly malformed but otherwise usable JSON structure, causing a cycle crash.
**Mitigation:** Wrap the decorated functions in a try-except block that logs the violation and triggers a graceful fallback or a specific `_alert_dot` notification, rather than allowing a hard crash.

**Confidence Score:** 9/10