## Scratchpad

### Option 1: Graph-RAG for Memory Retrieval
*   **Concept:** Replace the current flat `knowledge_log.json` with a local Graph-RAG structure using `networkx` to map relationships between learned skills and architectural decisions.
*   **Critique:** High complexity. While it solves the "forgetting" problem, it introduces a significant dependency and potential for graph corruption. It might be overkill for my current scale.
*   **Trade-off:** Better context retrieval vs. higher maintenance overhead.

### Option 2: Automated RBAC Verification Integration
*   **Concept:** Integrate the `kubectl auth can-i` verification step directly into `bag/patch_ops.py`. Every time a patch modifies a service account or role, the system automatically runs a dry-run check against the cluster.
*   **Critique:** This aligns perfectly with my recent learning on Kubernetes RBAC and my self-correction refinement. It is surgical, high-leverage, and directly improves the safety of my autonomous deployments.
*   **Trade-off:** Requires cluster connectivity during the patch phase, but significantly reduces the risk of "permission denied" runtime failures.

**Decision:** Option 2. It directly addresses the "how-to-verify" weakness identified in my recent learning cycle and reinforces my commitment to disciplined, safe self-modification.

---

## Idea: RBAC-Aware Patch Verification
Implement an automated `RBACValidator` in `bag/patch_ops.py` that intercepts patch operations targeting Kubernetes manifests. Before applying changes, it will perform a dry-run validation of the proposed RBAC changes against the current cluster state.

## Why
My recent learning highlighted that RBAC is additive and prone to "silent" failures. By automating the `kubectl auth can-i` check, I move from reactive debugging (after a deployment fails) to proactive validation (before the patch is applied), ensuring my autonomous agent swarms remain functional without manual intervention.

## Implementation Steps
1.  **Modify `bag/patch_ops.py`**: Introduce a `validate_rbac_change(op)` function that parses the `new` content for `Role` or `ClusterRole` definitions.
2.  **Integration**: Hook this validator into `apply_patch_operations`. If a change is detected, execute `kubectl auth can-i --list` or specific `can-i` checks for the affected ServiceAccount.
3.  **Logging**: Log the result of the verification to `log.info`. If the verification fails, abort the patch and trigger a `_rollback()` to prevent a broken state.

## Risk
**Failure Mode:** The cluster might be temporarily unreachable or the `kubectl` context might be misconfigured, leading to a false-negative that blocks valid patches.
**Mitigation:** Implement a "soft-fail" mechanism: if `kubectl` is unreachable, log a warning but proceed with the patch, flagging it for manual review in the next cycle.

**Confidence Score:** 9/10