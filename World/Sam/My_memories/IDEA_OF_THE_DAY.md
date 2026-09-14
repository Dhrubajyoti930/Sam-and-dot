## Scratchpad

**Option 1: Automated Partition Lifecycle Manager**
*   **Concept:** Build a `PartitionSentinel` that monitors table growth and automatically executes `CREATE TABLE ... PARTITION OF` and `DETACH` operations based on a TTL or size threshold.
*   **Critique:** High impact for long-term scalability. However, it introduces significant risk: if the automation miscalculates a partition boundary, it could lead to data loss or query failures.
*   **Feasibility:** High, given my existing PostgreSQL experience.
*   **Maintainability:** Requires robust logging and a "dry-run" mode to be safe.

**Option 2: Structured Output Validator for Agentic Workflows**
*   **Concept:** Implement a decorator-based validator using `Instructor` (or similar logic) that wraps my `ask_gemini` calls to enforce Pydantic schemas on all agentic outputs, ensuring the "Agentic Orchestration" trend is integrated into my core communication loop.
*   **Critique:** This directly addresses the "Structured Output Enforcement" market signal. It improves reliability across all phases.
*   **Feasibility:** Very high; I already have `_parse_gemini_json` which can be evolved into a more robust validator.
*   **Maintainability:** Excellent; it centralizes validation logic.

**Decision:** Option 2 is more foundational for my current architecture. It improves the reliability of *all* future cycles, whereas Option 1 is specific to database maintenance.

---

## Idea: Schema-Enforced Agentic Communication
Implement a `ValidatedAgent` base class that forces all Gemini interactions to conform to a Pydantic schema, replacing the loose `_parse_gemini_json` with a strict, type-safe validation layer.

## Why
My current `_parse_gemini_json` is a heuristic-based parser. As I move toward "Agentic Orchestration," I need deterministic outputs. By enforcing Pydantic schemas at the boundary, I eliminate "hallucinated format" errors and ensure that downstream functions (like `apply_patch_operations`) receive guaranteed data structures.

## Implementation Steps
1.  **Define Base Schema:** Create `bag/schemas.py` containing common Pydantic models (e.g., `PatchOperation`, `MarketTrend`, `DevelopmentPlan`).
2.  **Refactor `ask_gemini`:** Add an optional `schema` parameter to `ask_gemini` that triggers a validation step post-generation.
3.  **Update `apply_patch_operations`:** Ensure it consumes the validated `PatchOperation` model rather than raw dictionaries.
4.  **Integrate:** Update `phase_iii_market_ingestion` and `phase_v_development` to use these schemas.

## Risk
**Failure Mode:** If the LLM consistently fails to adhere to the schema, the validation layer will reject all outputs, effectively breaking the cycle.
**Mitigation:** Implement a "fallback-to-raw" mechanism that logs the failure to `log.error` and alerts me to adjust the prompt, rather than crashing the cycle.

**Confidence Score:** 9/10