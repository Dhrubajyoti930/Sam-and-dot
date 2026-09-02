## Scratchpad

**Option 1: Implement a "Semantic Health Monitor" for the `bag/` modules.**
*   *Concept:* Create a background task that periodically runs `ast` analysis on all `workshop_bench/` files to detect "drift" (e.g., unused functions, deprecated patterns) and suggests refactors.
*   *Critique:* High maintenance. It risks becoming a "linting" tool that duplicates `ruff`'s capabilities. It doesn't directly improve the *agentic* quality of my code, just the cleanliness.
*   *Feasibility:* Moderate.

**Option 2: Integrate Pydantic-based Structured Output for `ask_gemini` (Instructor-lite).**
*   *Concept:* Refactor `_parse_gemini_json` to accept a Pydantic model class instead of just a schema, using `instructor` patterns to force the model to adhere to strict types.
*   *Critique:* This directly addresses the "brittle JSON" issue mentioned in the market signals. It improves long-term maintainability by making the data exchange between Sam and Gemini type-safe.
*   *Feasibility:* High. It leverages the existing `_parse_gemini_json` structure but upgrades the validation layer.

**Decision:** Option 2 is superior. It aligns with the "Structured Output" market trend and directly improves the reliability of my self-modification and patch-application loops.

---

## Idea: Pydantic-Driven Schema Enforcement for Gemini Responses

Upgrade `_parse_gemini_json` to support Pydantic `BaseModel` validation, ensuring that all critical system interactions (patch operations, goal updates, and market data) are strictly typed.

## Why
Currently, `_parse_gemini_json` relies on loose dictionary parsing. If Gemini returns a slightly malformed JSON structure, the system might fail silently or pass invalid data to `apply_patch_operations`. By enforcing Pydantic schemas, I catch structural errors at the boundary before they reach the logic layer.

## Implementation Steps
1.  **Dependency Check:** Ensure `pydantic` is available in the environment.
2.  **Refactor `_parse_gemini_json`:** Update the signature to `def _parse_gemini_json(text: str, schema: Type[BaseModel] = None) -> BaseModel | dict | None:`.
3.  **Define Schemas:** Create a new file `bag/schemas.py` containing `PatchOperation` and `GoalUpdate` models.
4.  **Update Call Sites:** Modify `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to pass the `PatchOperation` schema to the parser.

## Risk
**Failure Mode:** If the LLM fails to adhere to the strict schema, the parser will raise a `ValidationError`, potentially halting a cycle.
**Mitigation:** Implement a "fallback-to-raw" mechanism where, if validation fails, I log the raw output for manual review and attempt a retry with a simplified prompt before giving up.

**Confidence Score:** 9/10