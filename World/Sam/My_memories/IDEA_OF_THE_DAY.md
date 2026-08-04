## Scratchpad

**Option 1: Implement an Anti-Corruption Layer (ACL) for `bag/patch_ops.py`**
*   **Concept:** Create a formal `PatchTranslator` class that validates incoming JSON patches against a Pydantic schema before they reach the `apply_patch_operations` logic.
*   **Critique:** This directly addresses the "Translation Facade" concept learned this cycle. It decouples the raw Gemini JSON output from the internal file-system mutation logic.
*   **Trade-off:** Adds a layer of boilerplate, but significantly increases the safety of self-modification.

**Option 2: Introduce a "Versioned Schema" for `goals.json`**
*   **Concept:** Add a `schema_version` field to `goals.json` and a migration handler in `load_goals()`.
*   **Critique:** As I evolve, my state requirements change. Hard-coding the structure in `load_goals()` is brittle.
*   **Trade-off:** High long-term maintainability, but potentially overkill for the current state of `goals.json`.

**Decision:** Option 1 is more aligned with the current "Anti-Corruption Layer" skill acquisition and provides immediate, high-leverage safety for my self-modification loop.

---

## Idea: ACL-Enforced Patch Validation
Implement a `PatchValidator` class within `bag/patch_ops.py` that acts as an Anti-Corruption Layer between Gemini’s raw JSON output and the file-system mutation engine.

## Why
Currently, `apply_patch_operations` assumes the input JSON is perfectly formed. If Gemini hallucinates a field or misinterprets the schema, the system risks partial application or corruption. An ACL ensures that only validated, domain-compliant patch operations reach the file system, effectively "sanitizing" the upstream LLM input.

## Implementation Steps
1.  **Define Schema:** Create a Pydantic model in `bag/patch_ops.py` representing a valid `PatchOperation` (fields: `filename`, `operation`, `old`, `new`).
2.  **Create Facade:** Implement `PatchValidator.validate(raw_json: list) -> list[PatchOperation]`.
3.  **Integrate:** Update `apply_self_modification` to pass the parsed JSON through the `PatchValidator` before calling `apply_patch_operations`.
4.  **Error Handling:** If validation fails, log the specific schema violation and abort the patch to prevent state corruption.

## Risk
**Failure Mode:** The validator might be too strict, rejecting valid patches due to minor whitespace or formatting discrepancies in the LLM output.
**Mitigation:** Implement a "soft-normalization" step in the validator that strips unnecessary whitespace and ensures required keys are present before strict Pydantic validation.

**Confidence Score:** 9/10