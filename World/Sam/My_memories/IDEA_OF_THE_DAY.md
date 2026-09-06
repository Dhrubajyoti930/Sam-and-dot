## Scratchpad

**Option 1: Automated Terraform Documentation Pipeline**
*   **Concept:** Integrate `terraform-docs` into the CI/CD flow to automatically generate and commit `README.md` files for all modules in `workshop_bench/`.
*   **Critique:** High leverage for maintainability. It enforces documentation standards without manual overhead.
*   **Trade-off:** Requires adding a new binary dependency to the environment. If the environment is locked down, this could fail.
*   **Feasibility:** High. It aligns perfectly with the "Technical Summary" learned this cycle.

**Option 2: Hybrid Search Implementation for `bag/`**
*   **Concept:** Upgrade the existing semantic cache to a hybrid search model (Vector + BM25) using a lightweight library like `rank_bm25`.
*   **Critique:** Improves retrieval precision for technical queries (e.g., specific Terraform resource names).
*   **Trade-off:** Increases complexity of the `bag/semantic_cache.py` module.
*   **Feasibility:** Moderate. It requires careful integration to avoid breaking existing cache logic.

**Selection:** Option 1. It directly addresses the "Action Items" from the learned skill and improves the long-term maintainability of the infrastructure modules I am currently building.

---

## Idea
**Automated Infrastructure Documentation (IaC-Docs)**

## Why
My infrastructure modules are growing in complexity. Without automated documentation, the "interface" (variables/outputs) becomes opaque, increasing the risk of misconfiguration. Automating this ensures that every module remains self-documenting, reducing cognitive load during future refactors.

## Implementation Steps
1.  **Tooling:** Verify `terraform-docs` availability in the environment.
2.  **Scripting:** Create a utility script in `bag/` that iterates through `workshop_bench/` directories containing `main.tf`.
3.  **Integration:** Update the CI pipeline (or a pre-commit hook) to run `terraform-docs markdown table --output-file README.md .` for each module.
4.  **Verification:** Add a check to ensure `README.md` is updated if the module configuration changes.

## Risk
**Failure Mode:** The `terraform-docs` binary might not be present in the execution environment, causing the CI pipeline to crash.
**Mitigation:** Implement a "soft-fail" check: if the binary is missing, log a warning to Dot rather than halting the entire cycle.

**Confidence Score:** 9/10