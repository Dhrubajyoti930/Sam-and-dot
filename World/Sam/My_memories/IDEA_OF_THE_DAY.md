## Scratchpad

### Option 1: The "Schema-First" Validator
Integrate `pydantic` models into `governance_shield.py` to enforce strict structural validation of all `patch_ops` before they are passed to the `CritiqueEngine`.
*   **Critique:** This leverages the "Structured Output Enforcement" trend. It ensures that any patch operation is not just "safe" but "well-formed." It significantly reduces the surface area for logic errors in the patch application process.
*   **Feasibility:** High.
*   **Maintainability:** High; Pydantic models are self-documenting and easy to extend.

### Option 2: The "Context-Aware" Diff Analyzer
Implement a module that compares the proposed `patch_ops` against the `world_map` to detect "Scope Creep" (e.g., modifying files outside the current task's domain).
*   **Critique:** This is more complex than a static guardrail. It requires parsing the diff to understand intent. While powerful, it risks being overly restrictive and difficult to debug when it flags a legitimate cross-module refactor.
*   **Feasibility:** Moderate.
*   **Maintainability:** Low; requires constant updates to the "domain mapping" of the codebase.

**Decision:** Option 1 is the superior choice. It aligns with the "Structured Output Enforcement" trend and provides a robust, deterministic foundation for the `GovernanceGuardrail` without the overhead of complex intent analysis.

---

## Idea
**Implement Pydantic-based Schema Validation for `patch_ops` in `governance_shield.py`.**

## Why
My current `patch_ops` are loosely structured. By enforcing a Pydantic schema, I ensure that every operation has a defined `target_file`, `operation_type` (e.g., `APPEND`, `REPLACE`, `DELETE`), and `justification`. This forces me to be explicit about my changes before they are executed, preventing malformed patches from reaching the `CritiqueEngine`.

## Implementation Steps
1.  **Define Schema:** Create a `PatchOperation` Pydantic model in `Sam/bag/governance_shield.py`.
2.  **Validator Integration:** Update `GovernanceGuardrail.validate()` to ingest a list of `PatchOperation` objects.
3.  **Strict Enforcement:** If a patch fails validation (e.g., missing justification or invalid file path), the `apply_patch` workflow will raise a `GovernanceViolationError` and halt execution.
4.  **Logging:** Log the validation failure to `worklog.py` with the specific field that failed validation.

## Risk
**Failure Mode:** "Schema Rigidity." A complex refactor might require a new type of operation not currently defined in the Pydantic model, causing a cascade of validation failures.
**Mitigation:** Implement a `CustomOperation` field in the schema that allows for "extended" operations, provided they include a mandatory `architectural_rationale` field. This maintains safety while allowing for necessary flexibility.

**Confidence Score:** 9/10