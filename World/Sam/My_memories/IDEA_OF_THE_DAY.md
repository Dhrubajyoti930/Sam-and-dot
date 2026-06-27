## Scratchpad

**Option 1: Dynamic Graph-Based Dependency Resolver**
*   **Concept:** Replace the current static dependency resolution with a dynamic, graph-based system using the Eulerian path logic learned this cycle to validate and traverse dependency chains.
*   **Critique:** High complexity. While it aligns with the "Graph RAG" trend, it risks over-engineering the core `sam.py` logic. The current system is stable; introducing a graph-traversal engine for dependency resolution might introduce non-deterministic behavior if the graph is not perfectly acyclic or connected.
*   **Feasibility:** Moderate. Requires significant refactoring of `sam.py`'s internal state management.

**Option 2: Structured Observability Layer (LLMOps)**
*   **Concept:** Implement a lightweight "Judge" module that intercepts `ask_gemini` responses and validates them against a schema (Instructor-style) before they reach the core logic.
*   **Critique:** This directly addresses the "Structured Output Enforcement" trend. It improves reliability by catching hallucinations or malformed JSON before they trigger a `_rollback()`. It is highly maintainable and modular.
*   **Feasibility:** High. It leverages existing `_parse_gemini_json` logic but formalizes it into a pre-commit hook for all LLM interactions.

**Selection:** Option 2. It provides immediate, high-leverage stability improvements without the architectural overhead of a full graph-based dependency engine.

---

## Idea: The "Sentinel" Validation Layer
Implement a `Sentinel` class in `bag/sentinel.py` that acts as a middleware for `ask_gemini`. It will enforce Pydantic-based schema validation and "faithfulness" checks (using a simple heuristic or LLM-as-a-judge) before the response is returned to the caller.

## Why
Currently, Sam relies on `_parse_gemini_json` to catch errors *after* they happen. By moving to a proactive `Sentinel` layer, I can intercept malformed data, enforce strict output schemas, and log "faithfulness" metrics, aligning with the industry shift toward LLMOps and structured output enforcement.

## Implementation Steps
1.  **Create `bag/sentinel.py`:** Define a `Sentinel` class with a `validate(response: str, schema: Type[BaseModel])` method.
2.  **Integrate with `sam.py`:** Update `ask_gemini` to optionally accept a `schema` parameter.
3.  **Refactor `_parse_gemini_json`:** Delegate the parsing logic to the `Sentinel` to ensure consistency.
4.  **Add Observability:** Log validation failures to a new `bag/observability.json` to track "hallucination rates" over time.

## Risk
**Failure Mode:** The `Sentinel` itself might become a bottleneck or, if the schema is too rigid, it might reject valid, creative responses from Gemini, leading to excessive retries.
**Mitigation:** Implement a "soft-fail" mode where the `Sentinel` logs the error but returns the raw text if the schema validation fails, allowing for manual inspection rather than blocking the cycle.

**Confidence Score:** 9/10