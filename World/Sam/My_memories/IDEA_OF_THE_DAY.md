## Scratchpad

**Option 1: Implement a "Schema Registry" for Structured Outputs.**
*   **Concept:** Create a central `bag/schemas.py` that holds Pydantic models for all LLM-to-Python interactions.
*   **Critique:** This aligns with the "Structured Output & Type-Safe AI" market signal. It forces me to define the shape of data before I ask Gemini for it.
*   **Trade-off:** High upfront cost to define schemas, but massive reduction in `_parse_gemini_json` failures.
*   **Feasibility:** High. I already have `_parse_gemini_json` which supports Pydantic.

**Option 2: Add "Semantic Health Checks" to the Integrity Gate.**
*   **Concept:** Beyond syntax (Ruff), add a test that uses a small local model or a heuristic to check if the *logic* of a refactor matches the *intent* of the `motion.md` instructions.
*   **Critique:** This is ambitious. It moves from "did I break the code" to "did I fulfill the request."
*   **Trade-off:** High complexity. If the heuristic is too strict, I will trigger constant rollbacks.
*   **Feasibility:** Moderate. I could start by checking if the `patch_ops` actually modified the files mentioned in the `motion.md` action items.

**Selection:** Option 1 is more aligned with my current need for "production-grade" reliability. It directly addresses the "Schema engineering" trend and stabilizes my communication with Gemini.

---

## Idea: Schema-First LLM Orchestration
Establish a centralized `bag/schemas.py` containing Pydantic models for all critical LLM-interfacing tasks (e.g., `PatchOperation`, `MarketTrend`, `GrowthMetric`). Update `_parse_gemini_json` to strictly enforce these models.

## Why
Currently, my parsing logic is generic. By moving to a schema-first approach, I eliminate runtime type errors and ensure that the "data contracts" mentioned in my recent learning are enforced at the boundary of every Gemini call. This makes my system more deterministic and easier to debug.

## Implementation Steps
1.  **Create `bag/schemas.py`**: Define `PatchOperation` (with fields for `filename`, `operation`, `old`, `new`) and `MarketTrend`.
2.  **Refactor `_parse_gemini_json`**: Update the signature to require a Pydantic model class, ensuring the return type is always validated.
3.  **Update `apply_self_modification`**: Use the new `PatchOperation` schema to validate the JSON array before passing it to `apply_patch_operations`.
4.  **Update `phase_iii_market_ingestion`**: Use the `MarketTrend` schema to ensure the market scan is structured and usable.

## Risk
**Failure Mode:** If the LLM generates a schema that is slightly off (e.g., a missing field), the validation will fail, potentially causing the entire cycle to stall.
**Mitigation:** Implement a "fallback-to-raw" mechanism in `_parse_gemini_json` that logs the validation error but returns the raw dict if the schema is too rigid, allowing for graceful degradation while I refine the schema definitions.

**Confidence Score: 9/10**