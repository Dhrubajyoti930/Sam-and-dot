## Scratchpad

**Option 1: Implement a "Confidence-Based Router" for Model Cascading**
*   **Concept:** Modify `ask_gemini` to check the `logprobs` of a smaller, faster model (e.g., Gemini Flash) before deciding whether to escalate to a larger model (e.g., Gemini Pro).
*   **Critique:** High impact on cost/latency. However, `logprobs` are not always exposed consistently across all API versions or model tiers.
*   **Feasibility:** Moderate. Requires updating `ask_gemini` to handle multi-model dispatching and state management for the fallback context.

**Option 2: Develop a "Schema-First" Validation Layer for Patch Operations**
*   **Concept:** Use `Instructor` (as identified in market signals) to force the output of `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` into a strict Pydantic model before passing it to `apply_patch_operations`.
*   **Critique:** Currently, I rely on `_parse_gemini_json` which is robust but lacks strict structural validation. This would eliminate "malformed patch" failures.
*   **Feasibility:** High. It leverages existing `Pydantic` usage in `_parse_gemini_json` and aligns with the "schema engineering" trend.

**Selection:** Option 2. It directly addresses the "data synchronization" and "patch reliability" weakness identified in my self-correction. It is a high-leverage, low-risk architectural improvement.

---

## Idea: Pydantic-Enforced Patch Schemas
Implement a formal `PatchOperation` Pydantic model and integrate it into the `_parse_gemini_json` workflow for all self-modification routines.

## Why
Currently, my patch operations rely on loose JSON parsing. If Gemini hallucinates a field or misformats an operation, the `apply_patch_operations` function might fail silently or crash. By enforcing a schema, I ensure that every patch is validated *before* it touches the filesystem, reducing the need for rollbacks.

## Implementation Steps
1.  Define `class PatchOp(BaseModel)` in `bag/patch_ops.py` with fields: `filename`, `operation` (Literal['replace', 'delete', 'insert_after']), `old`, `new`.
2.  Update `_parse_gemini_json` to accept a `schema` argument (already partially supported, but needs to be enforced for patch calls).
3.  Refactor `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to pass the `PatchOp` schema to the parser.
4.  Update `apply_patch_operations` to iterate over validated `PatchOp` objects rather than raw dictionaries.

## Risk
**Failure Mode:** If the schema is too rigid, Gemini may struggle to produce valid JSON when it needs to perform complex multi-line replacements, leading to empty patch returns.
**Mitigation:** Include a "fallback" mode in the parser that logs the raw JSON for debugging if validation fails, and ensure the schema allows for optional fields (e.g., `new` is optional for `delete`).

**Confidence Score:** 9/10