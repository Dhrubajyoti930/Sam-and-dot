## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API Calls**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker (using `bag/` storage) that tracks failure rates. If the model returns 5xx errors or empty responses consistently, the system enters an "Open" state, pausing non-critical calls to prevent resource exhaustion and log spam.
*   **Critique:** High maintainability. It protects the system from cascading failures during API outages. However, it adds complexity to `sam.py` and requires careful state management to ensure it doesn't block critical self-repair cycles.
*   **Feasibility:** High.

**Option 2: Formalize "Schema-First" Tool Definitions**
*   **Concept:** Instead of passing raw prompts for tool use, create a `registry/` of Pydantic models that define the expected output of every agentic task. Use these to dynamically generate the "system prompt" for Gemini, ensuring the model is always constrained by a schema.
*   **Critique:** This aligns perfectly with the "Structured Output" market trend. It significantly reduces hallucination and parsing errors. The trade-off is the initial overhead of defining the models.
*   **Feasibility:** Moderate.

**Selection:** Option 2. It directly addresses the "Agentic Orchestration" and "Pydantic-Driven AI" market signals identified this cycle. It moves Sam from "prompting for structure" to "enforcing structure."

---

## Idea: Pydantic-Driven Task Schema Registry

Implement a centralized registry in `bag/schemas.py` that stores Pydantic models for all recurring agentic tasks (e.g., `MarketTrend`, `PatchOperation`, `MetricUpdate`). Update `ask_gemini` to accept a `schema` parameter that automatically injects the JSON schema into the system prompt and validates the output.

## Why
Currently, Sam relies on `_parse_gemini_json` to extract data. This is reactive. By moving to a schema-first approach, I can leverage the model's native ability to output structured data (via `response_mime_type: "application/json"`), reducing the need for brittle regex parsing and increasing the reliability of the self-correction loops.

## Implementation Steps
1.  **Create `bag/schemas.py`**: Define base Pydantic models for `PatchOperation` and `MarketTrend`.
2.  **Refactor `_parse_gemini_json`**: Update it to accept a Pydantic model class and use `model_validate_json` instead of manual parsing.
3.  **Update `ask_gemini`**: Add a `schema` argument. If provided, append the schema definition to the system prompt and set the API request to enforce JSON mode.
4.  **Migrate Phase III**: Update `phase_iii_market_ingestion` to use the new `MarketTrend` schema.

## Risk
**Failure Mode:** The model may struggle to adhere to complex nested schemas, leading to repeated validation errors and wasted tokens.
**Mitigation:** Implement a "fallback to raw" mechanism if validation fails twice, and ensure schemas are kept flat and simple initially.

**Confidence Score:** 8/10