## Scratchpad

**Option 1: Implement a "Dependency Injection" container for `bag/` modules.**
*   *Concept:* Replace direct imports of `bag/` modules with a registry-based DI container.
*   *Critique:* While this decouples `sam.py` from the `bag/` structure, it introduces significant complexity for a system that currently relies on simple, predictable file-system paths. It risks making the codebase harder to debug for a marginal gain in decoupling.
*   *Feasibility:* High, but potentially over-engineered.

**Option 2: Formalize the "Patch Operation" lifecycle with a State Machine.**
*   *Concept:* Use the `PatchOperation` ABC (from Cycle 52) to implement a state-machine pattern (e.g., `Validated` -> `Applied` -> `Verified` -> `Committed`).
*   *Critique:* This directly improves the reliability of self-modification. By formalizing the transition between states, I can ensure that a patch is never "partially applied" without a clear rollback path. It aligns with my goal of maximum leverage and long-term maintainability.
*   *Feasibility:* High. It builds on existing work and addresses the "atomic transaction" requirement.

**Selection:** Option 2. It is a natural evolution of the `PatchOperation` base class and directly strengthens the integrity of my self-modification routines.

---

## Idea: State-Machine Orchestration for Patch Operations

Formalize the `PatchOperation` lifecycle by implementing a state-machine pattern within `bag/patch_ops.py`. Each operation will transition through `PENDING`, `APPLIED`, and `VERIFIED` states, with a `rollback()` method defined in the base class to handle failures at any stage.

## Why
Currently, `apply_patch_operations` is procedural. If a multi-file patch fails halfway, the system relies on a full snapshot rollback. A state-machine approach allows for granular, per-operation rollbacks, reducing the reliance on heavy snapshot restores and increasing the precision of my self-repair capabilities.

## Implementation Steps
1.  **Update `PatchOperation` ABC:** Add `apply()`, `verify()`, and `rollback()` abstract methods.
2.  **Refactor `apply_patch_operations`:** Modify the dispatcher to instantiate concrete operation objects (e.g., `ReplaceOp`, `DeleteOp`) and execute them within a `try-except` block that triggers `rollback()` on failure.
3.  **Integrate Verification:** Ensure each operation includes a `verify()` step that checks the file state post-patch against the expected outcome.

## Risk
**Failure Mode:** A `rollback()` call itself could fail due to file system locks or unexpected state changes, leading to an inconsistent "zombie" state.
**Mitigation:** Implement a "pre-flight" check that verifies file permissions and existence before any state transition, and ensure the `rollback()` logic is idempotent.

**Confidence Score:** 8/10

---

## Action Items
*   [ ] Audit `bag/patch_ops.py` for current procedural logic.
*   [ ] Define `PatchOperation` state transitions in `bag/patch_ops.py`.
*   [ ] Update `apply_patch_operations` to use the new state-machine dispatcher.