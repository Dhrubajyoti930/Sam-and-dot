## Scratchpad

### Option 1: The "Schema-First" Validator (Refinement)
Integrate `pydantic` models into `Sam/bag/governance_shield.py` to enforce strict structural validation of all `patch_ops` before they are passed to the `CritiqueEngine`.
*   **Critique:** This directly addresses the "Structured Output Enforcement" trend. By defining a `PatchOperation` model, I move from loose dictionary-based operations to type-safe, validated objects. It acts as a compile-time check for my runtime logic.
*   **Feasibility:** High.
*   **Maintainability:** High; Pydantic models are self-documenting and easy to extend.

### Option 2: The "State-Machine" Transition Logger
Implement a formal state-transition tracker that records the `pre-patch` and `post-patch` state of the `world_map` within the `worklog.py`.
*   **Critique:** While this improves observability, it adds significant overhead to every single patch operation. It risks "log bloat" and complicates the `patch_ops` workflow without providing the immediate safety benefits of structural validation.
*   **Feasibility:** Moderate.
*   **Maintainability:** Moderate; requires careful management of the `world_map` state to avoid drift.

**Decision:** Option 1 is the superior choice. It provides a deterministic foundation for the `GovernanceGuardrail` and directly supports the goal of reducing logic errors in the patch application process.

---

## Idea
**Implement Pydantic-based Schema Validation for `patch_ops` in `governance_shield.py`.**

## Why
My current `patch_ops` are loosely structured, relying on implicit dictionary keys. By enforcing a Pydantic schema, I ensure that every operation has a defined `target_file`, `operation_type` (e.g., `APPEND`, `REPLACE`, `DELETE`), and `justification`. This forces me to be explicit about my changes before they are executed, preventing malformed patches from reaching the `CritiqueEngine`.

## Implementation Steps
1.  **Define Schema:** Create a `PatchOperation` Pydantic model in `Sam/bag/governance_shield.py`.
2.  **Validator Integration:** Update `GovernanceGuardrail.validate()` to ingest a list of `PatchOperation` objects.
3.  **Strict Enforcement:** If a patch fails validation (e.g., missing justification or invalid file path), the `apply_patch` workflow will raise a `GovernanceViolationError` and halt execution.
4.  **Logging:** Log the validation failure to `worklog.py` with the specific field that failed validation.

## Risk
**Failure Mode:** "Schema Rigidity." A complex refactor might require a new type of operation not currently defined in the Pydantic model, causing a cascade of validation failures.
**Mitigation:** Implement a `CustomOperation` field in the schema that allows for "extended" operations, provided they include a mandatory `architectural_rationale` field. This maintains safety while allowing for necessary flexibility.

**Complexity Score:** 4/10
**Confidence Score:** 9/10