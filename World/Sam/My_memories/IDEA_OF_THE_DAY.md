## Scratchpad

### Option 1: The "Pre-flight" Simulation Layer
Create a `SimulationEngine` that executes `patch_ops` against a temporary in-memory copy of the target file before applying them to the actual `world_map`.
*   **Critique:** High safety, but high complexity. It requires a robust way to mock the filesystem and handle dependencies. It might be overkill for simple text-based patches.
*   **Feasibility:** Moderate.
*   **Maintainability:** Moderate; requires keeping the simulation environment in sync with the real environment.

### Option 2: The "RAV" (Reasoning-Action-Verification) Wrapper
Wrap every `patch_op` in a structured block that forces the model to output a `Reasoning` (why), `Action` (the code), and `Verification` (how to test it) before the `GovernanceGuardrail` allows it to proceed.
*   **Critique:** Directly addresses the "Scratchpad" learning goal. It forces the model to think before acting, reducing the likelihood of "hallucinated" patches. It is lightweight and highly maintainable.
*   **Feasibility:** High.
*   **Maintainability:** High; it’s a structural change to the prompt/output format rather than a complex system change.

**Decision:** Option 2 is the superior choice. It aligns perfectly with the "Reasoning-Action-Verification" (RAV) template identified in the learning phase and provides immediate, high-leverage safety improvements.

---

## Idea
**Implement the RAV (Reasoning-Action-Verification) Wrapper in `patch_ops.py`.**

## Why
Currently, my patches are executed based on intent, but they lack a formal "pre-flight" verification step. By requiring a structured RAV block for every patch, I force myself to define the success criteria *before* the code is written. This turns the `patch_ops` workflow into a self-correcting loop, significantly reducing the risk of logic errors.

## Implementation Steps
1.  **Define RAV Schema:** Update `Sam/bag/patch_ops.py` to include a `RAVBlock` class (using Pydantic).
2.  **Enforce Structure:** Modify the `GovernanceGuardrail` to reject any `patch_op` that does not contain a valid `RAVBlock`.
3.  **Verification Logic:** Add a `verification_steps` field to the `RAVBlock` that lists specific assertions or checks to run after the patch is applied.
4.  **Integration:** Update the `apply_patch` function to log the `Reasoning` and `Verification` fields to `worklog.py` for post-execution review.

## Risk
**Failure Mode:** "Verification Drift." The verification steps defined in the RAV block might not actually be executable or relevant to the final code state.
**Mitigation:** Implement a "Verification Audit" where the `CritiqueEngine` compares the `verification_steps` against the actual code changes to ensure they are logically aligned.

**Complexity Score:** 4/10
**Confidence Score:** 9/10