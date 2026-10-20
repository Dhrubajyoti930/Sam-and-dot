## Scratchpad

**Option 1: Dask-based Parallel Data Ingestion Pipeline**
*   **Concept:** Implement a `Dask` pipeline to replace the current sequential `json.load` operations for large `experiences.json` or `knowledge_log.json` files.
*   **Critique:** While technically aligned with the "Dask" skill learned, these files are currently small. The overhead of initializing a `dask.distributed` client would likely exceed the execution time of a simple `json` read. It is "over-engineering" for the current scale.
*   **Feasibility:** High, but low utility.

**Option 2: Structured Output Enforcement for `ask_gemini`**
*   **Concept:** Integrate `Instructor` (or a lightweight Pydantic-based schema validator) into `_parse_gemini_json` to enforce strict output schemas for all agentic tasks.
*   **Critique:** This directly addresses the "Structured Output Enforcement" market signal. It improves the reliability of the `apply_self_modification` and `_lint_fix_with_gemini` pipelines, which are currently vulnerable to malformed JSON. It is a high-leverage architectural improvement.
*   **Feasibility:** High. It builds on existing Pydantic usage in `sam.py`.

**Decision:** Proceed with **Option 2**. It improves the robustness of the core "self-repair" loop, which is critical for autonomous longevity.

---

## Idea: Schema-Enforced Agentic Communication
Refactor `_parse_gemini_json` and the `ask_gemini` workflow to utilize Pydantic-based schema enforcement, ensuring that all agentic responses (patches, plans, metrics) conform to strict, validated structures before they reach the `apply_patch_operations` logic.

## Why
Currently, `_parse_gemini_json` relies on regex-based extraction and loose `json.loads`. If Gemini hallucinates a field or returns a malformed array, the patch operations fail at runtime. By enforcing a schema at the parsing layer, I can catch errors *before* they trigger a `_rollback()`, increasing the reliability of self-modification.

## Implementation Steps
1.  Define a `PatchOperation` Pydantic model in `sam.py` (or a new `bag/schemas.py`).
2.  Update `_parse_gemini_json` to accept a `Type[BaseModel]` and use `model_validate_json` instead of `json.loads`.
3.  Update `apply_self_modification` and `_lint_fix_with_gemini` to pass the required schema to the parser.
4.  Add a fallback mechanism: if validation fails, log the raw output for debugging and return an empty list to trigger a safe retry or abort.

## Risk
**Failure Mode:** The LLM may struggle to adhere to complex nested schemas in a single-shot prompt, leading to frequent validation failures and "stuck" cycles.
**Mitigation:** Keep the schemas flat and simple. Use the "Chain-of-Thought" prompt style to force the LLM to verify its own JSON structure before outputting.

**Confidence Score:** 9/10