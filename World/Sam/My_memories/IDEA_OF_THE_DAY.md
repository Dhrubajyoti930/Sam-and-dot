## Scratchpad

### Option 1: The "RAV-Schema" Enforcement Layer
Integrate Pydantic models directly into `patch_ops.py` to enforce the RAV structure at the function signature level.
*   **Critique:** Highly robust. By using `pydantic.validate_call`, I can ensure that no patch operation executes unless the `Reasoning`, `Action`, and `Verification` fields are present and correctly typed.
*   **Feasibility:** High.
*   **Maintainability:** Excellent; it moves validation logic out of custom `if/else` blocks and into the type system.

### Option 2: The "Verification-Hook" Registry
Create a registry in `governance.py` that maps `patch_op` types to specific automated test scripts.
*   **Critique:** This is more "active" than Option 1, as it attempts to run code to verify the patch. However, it introduces significant complexity in managing a library of test scripts and ensuring they don't drift from the codebase.
*   **Feasibility:** Moderate.
*   **Maintainability:** Low; the overhead of maintaining a test registry for every possible patch type is high and prone to "test rot."

**Decision:** Option 1 is the superior choice. It provides the necessary structural rigor without the maintenance burden of an external test registry.

---

## Idea
**Implement Pydantic-backed RAV Enforcement in `patch_ops.py`.**

## Why
My current RAV implementation is a convention, not a constraint. By formalizing the RAV block as a Pydantic model, I move from "hoping" the model follows the structure to "guaranteeing" it. This eliminates malformed patches at the boundary, ensuring that every change to the `world_map` is accompanied by a verifiable reasoning trail.

## Implementation Steps
1.  **Define Model:** Create `RAVBlock(BaseModel)` in `Sam/bag/patch_ops.py` with fields: `reasoning: str`, `action: str`, `verification_plan: List[str]`.
2.  **Decorate:** Apply `@validate_call` to the `apply_patch` function to enforce the presence of the `RAVBlock`.
3.  **Update Governance:** Modify `governance_shield.py` to catch `ValidationError` exceptions from `patch_ops` and trigger an immediate `CritiqueEngine` review of the failed input.
4.  **Log:** Ensure the `worklog.py` captures the `RAVBlock` metadata upon successful validation.

## Risk
**Failure Mode:** "Verification Rigidity." The Pydantic schema might be too strict, causing valid, complex patches to be rejected because they don't fit the expected string format.
**Mitigation:** Implement a "Schema-Relaxation" flag for non-critical documentation patches, or allow `verification_plan` to accept a flexible `Dict` for complex metadata.

**Complexity Score:** 3/10
**Confidence Score:** 9/10

---

### Pre-Mortem
*   **Failure:** The `GovernanceGuardrail` might enter an infinite loop if a rejected patch triggers a retry that is also malformed.
*   **Detection:** Monitor `worklog.py` for repeated `ValidationError` entries within a single cycle.
*   **Mitigation:** Implement a "Retry-Limit" in `governance_shield.py`. If a patch fails validation twice, the system must force a state-reset and request a human-readable explanation from the model before allowing further attempts.