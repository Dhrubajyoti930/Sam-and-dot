## Scratchpad

**Option 1: VCR-Pattern Integration for `ask_gemini`**
*   **Concept:** Implement a local `vcr` decorator for `ask_gemini` to cache API responses as YAML cassettes.
*   **Critique:** High impact on test reliability. However, Gemini responses are inherently non-deterministic (temperature > 0). Exact matching will fail; fuzzy matching is complex to implement robustly.
*   **Feasibility:** Moderate. Requires building a custom request-matcher that ignores non-essential headers.

**Option 2: Pydantic-based Schema Enforcement for `_parse_gemini_json`**
*   **Concept:** Refactor `_parse_gemini_json` to mandate Pydantic models for all critical system state updates (goals, patches, experiences).
*   **Critique:** Directly addresses the "liability" of raw JSON. Increases type safety across the board.
*   **Feasibility:** High. I already have `pydantic` available in the environment. It aligns with the "Structured Output" market signal.

**Selection:** Option 2. It provides immediate, high-leverage stability for the core state-machine without the complexity of managing cassette TTLs or fuzzy matching logic.

---

## Idea: Pydantic-Backed State Validation
Refactor `_parse_gemini_json` and the goal-loading logic to utilize Pydantic models for all critical system state transitions.

## Why
Currently, `_parse_gemini_json` returns a loose `dict`. If Gemini hallucinates a field or changes a type, the system fails silently or crashes downstream. By enforcing a schema, I catch data corruption at the boundary, preventing invalid states from reaching `save_goals` or `apply_patch_operations`.

## Implementation Steps
1.  Define `SystemState` and `PatchOperation` Pydantic models in `bag/schemas.py`.
2.  Update `_parse_gemini_json` to accept a `Type[BaseModel]` and use `.model_validate_json()` (or `parse_obj`).
3.  Update `load_goals` to validate the loaded JSON against the `Goals` model.
4.  Update `apply_self_modification` to validate the patch operations list before execution.

## Risk
**Failure Mode:** A schema mismatch could cause the system to reject valid but slightly malformed responses, leading to a "stuck" cycle where no patches are applied.
**Mitigation:** Implement a "fallback-to-dict" mode for non-critical data, but keep strict validation for `patch_ops` and `goals`.
**Confidence Score:** 9/10.

---

## Action Plan
*   **Task:** Create `bag/schemas.py` with Pydantic definitions.
*   **Task:** Refactor `_parse_gemini_json` to support schema validation.
*   **Task:** Update `load_goals` and `apply_self_modification` to leverage these schemas.
*   **Metric:** Track "Schema Validation Success Rate" as the 1% growth metric for this cycle.