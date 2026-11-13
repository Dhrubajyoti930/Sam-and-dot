## Scratchpad

**Option 1: Pydantic-Driven Schema Enforcement for Market Ingestion**
*   **Concept:** Replace raw JSON parsing in `phase_iii_market_ingestion` with a strict Pydantic model validation layer.
*   **Critique:** High feasibility. It directly addresses the "hallucination detection" skill learned this cycle. It improves reliability by failing fast if the LLM returns malformed data.
*   **Trade-off:** Adds a dependency on Pydantic (if not already present) and requires defining schemas for each trend type.
*   **Maintainability:** High. Schema-as-code is self-documenting.

**Option 2: Semantic Anchoring for Market Signals**
*   **Concept:** Integrate `all-MiniLM-L6-v2` to compute cosine similarity between the fetched market signal and the original query intent.
*   **Critique:** Higher complexity. Requires managing a local embedding model or an API call. Might be overkill for a "Fast-Path" scan.
*   **Trade-off:** Significant latency increase per cycle.
*   **Maintainability:** Moderate. Requires maintaining an embedding pipeline.

**Decision:** Option 1 is the superior "minimal footprint, maximum leverage" choice. It provides immediate structural integrity without the heavy compute overhead of embedding models, aligning with the "Fast-Path" refinement in my implementation plan.

---

## Idea: Pydantic-Schema Enforcement for Market Ingestion

Implement a `MarketSignal` Pydantic model to validate the output of `phase_iii_market_ingestion`. This ensures that all ingested market trends conform to a strict schema (Title, Category, Description, ConfidenceScore) before they reach the synthesis phase.

## Why
"Vibe-based" data ingestion is a liability. By enforcing a schema, I eliminate downstream errors caused by missing fields or hallucinated data structures. This directly supports the "Structured Output & Pydantic-Driven AI" market trend and improves the reliability of my `bag/` storage.

## Implementation Steps
1.  Define `MarketSignal` and `MarketReport` (a list of signals) models in a new `bag/schemas.py`.
2.  Update `_parse_gemini_json` in `sam.py` to accept an optional `schema` argument (already partially implemented, needs refinement).
3.  Modify `phase_iii_market_ingestion` to pass the `MarketReport` schema to the parser.
4.  If validation fails, log the error and return an empty list rather than corrupting the synthesis phase with partial data.

## Risk
**Failure Mode:** The LLM may struggle to adhere to the schema if the prompt is too restrictive, leading to frequent validation failures and empty ingestion cycles.
**Mitigation:** Provide a "few-shot" example of the expected JSON structure within the `PHASE_III_PROMPT` to guide the model's output formatting.

**Confidence Score:** 9/10