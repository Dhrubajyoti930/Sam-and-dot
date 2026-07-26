## Scratchpad

**Option 1: Implement KL-Divergence Loss for Model Distillation**
*   **Concept:** Add a `DistillationLoss` class to `bag/training_utils.py` that computes the KL divergence between teacher and student logits.
*   **Critique:** High alignment with the "Model Distillation" skill learned this cycle. It is a surgical, high-leverage addition.
*   **Trade-off:** Requires a teacher model to be available in the environment. If I don't have a teacher model loaded, this code sits dormant.
*   **Feasibility:** High. PyTorch's `nn.KLDivLoss` is standard.

**Option 2: Integrate Instructor for Structured Output**
*   **Concept:** Refactor `_parse_gemini_json` to use `instructor` for Pydantic-based validation instead of manual regex/parsing.
*   **Critique:** Directly addresses the "Structured Output" market trend. It replaces fragile regex with robust, type-safe schema enforcement.
*   **Trade-off:** Introduces a new dependency (`instructor`). I must ensure it doesn't bloat the environment or conflict with existing `pydantic` versions.
*   **Feasibility:** High. It simplifies the `_parse_gemini_json` logic significantly.

**Decision:** I will proceed with **Option 2**. It provides immediate, tangible improvements to the reliability of my core communication loop with Gemini, which is the foundation of all other phases.

---

## Idea: Transition to `instructor` for Structured Output

Refactor `_parse_gemini_json` in `sam.py` to leverage the `instructor` library for LLM-to-Pydantic mapping, replacing the current regex-based extraction.

## Why
My current `_parse_gemini_json` relies on regex to find JSON boundaries. This is brittle when Gemini includes conversational filler or malformed markdown. `instructor` handles the extraction, validation, and retries natively, ensuring that my internal state updates (like `goals.json` or `patch_ops`) are always type-safe and schema-compliant.

## Implementation Steps
1.  **Dependency Check:** Verify `instructor` is available in the environment.
2.  **Refactor `sam.py`:** Update `_parse_gemini_json` to accept a Pydantic model class and use `instructor.patch(CLIENT).chat.completions.create(...)` or the equivalent `from_response` pattern.
3.  **Schema Definition:** Define a `PatchOperation` Pydantic model in `bag/patch_ops.py` to enforce the structure of patch operations.
4.  **Validation:** Run `self_check()` to ensure the new imports don't break existing logic.

## Risk
**Failure Mode:** The `instructor` library might introduce latency or dependency conflicts with the existing `google-genai` client.
**Mitigation:** I will perform a dry-run of the import and a simple schema validation test before fully replacing the existing regex logic. If `instructor` fails to initialize, I will revert to the regex fallback.

**Confidence Score:** 9/10