## Scratchpad

**Option 1: Federated Learning Simulation (from Action Items)**
*   **Concept:** Implement a `FedAvg` loop in `workshop_bench/` using a local dataset split.
*   **Critique:** High technical value for understanding decentralized ML. However, it is a "toy" implementation. It doesn't directly improve my core architecture or operational efficiency. It risks being a "shiny object" that consumes cycles without yielding a production-grade improvement to my own self-improvement loop.
*   **Feasibility:** High.

**Option 2: Pydantic-Driven "Schema-First" Patching**
*   **Concept:** Refactor `bag/patch_ops.py` to use Pydantic models for the `patch_operations` JSON schema. Currently, I rely on loose dictionary parsing.
*   **Critique:** This aligns perfectly with my recent shift toward Pydantic-backed structured planning (Cycle 559). It increases the robustness of my self-modification loop, making it harder to inject malformed patches. It is a high-leverage, long-term maintainability win.
*   **Feasibility:** High.

**Decision:** Option 2. It directly strengthens the "Integrity Gate" and reduces the likelihood of future `_rollback()` events caused by malformed patch JSON.

---

## Idea
**Schema-Enforced Patch Transactions**

## Why
My current patch application relies on loose JSON parsing. As I increase the complexity of my self-modifications, the risk of a malformed patch operation (e.g., missing keys, invalid operation types) increases. By formalizing the patch structure into a Pydantic model, I move validation from "runtime failure" to "schema-validation failure," allowing me to catch errors before `apply_patch_operations` is even invoked.

## Implementation Steps
1.  Define a `PatchOperation` Pydantic model in `bag/patch_ops.py` with strict field validation (e.g., `Literal` for operations, `Path` for filenames).
2.  Update `apply_patch_operations` to accept a list of these validated models instead of raw dictionaries.
3.  Modify `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to pass the generated JSON through this validator before attempting to apply the patch.
4.  Add a unit test in `bag/tests.py` to verify that invalid patch JSON is rejected by the validator.

## Risk
**Failure Mode:** The Pydantic model might be too rigid, causing valid but slightly non-standard patch operations to fail, leading to a "stuck" state where I cannot apply necessary fixes.
**Mitigation:** Implement a "fallback" mode where, if validation fails, I log the specific schema violation and alert Dot, rather than simply crashing. I will also keep the model definition extensible.

**Confidence Score:** 9/10