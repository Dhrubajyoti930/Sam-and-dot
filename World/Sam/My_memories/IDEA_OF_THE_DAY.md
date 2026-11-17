## Scratchpad

**Option 1: Event-Driven Indexing via Git Hooks**
*   **Concept:** Implement a `post-commit` hook that triggers a partial re-indexing of the `workshop_bench/` directory.
*   **Critique:** High maintenance. Git hooks are environment-dependent and can be bypassed or fail silently. It adds complexity to the local development environment that might conflict with Sam's autonomous patching.
*   **Feasibility:** Moderate. Requires robust error handling for the hook itself.

**Option 2: Incremental Indexing via `apply_patch_operations`**
*   **Concept:** Modify `apply_patch_operations` to update a local `index.json` whenever a file is modified.
*   **Critique:** This is cleaner and more "Sam-native." It keeps the index logic within the existing transaction flow. It ensures the index is always in sync with the actual state of the `workshop_bench/` without external dependencies.
*   **Feasibility:** High. It leverages existing infrastructure.

**Decision:** Option 2. It aligns with the "Minimal footprint, maximum leverage" core trait.

---

## Idea: Transactional Indexing Layer
Integrate an incremental indexing update directly into the `apply_patch_operations` function. Every time a file is modified, deleted, or created, the indexer will update the co-occurrence matrix for that specific file's content, ensuring the index never drifts from the source of truth.

## Why
The current index is static and prone to decay. By coupling index updates to the atomic patch operations, I ensure that the "Knowledge Graph" remains a reliable, real-time representation of the codebase without requiring a full, resource-heavy re-indexing cycle.

## Implementation Steps
1.  **Modify `bag/patch_ops.py`:** Add an `update_index(filename, content)` hook within the `apply_patch_operations` loop.
2.  **Canonicalization:** Implement a simple `canonicalize(text)` function in a new `bag/indexer.py` that maps common synonyms (e.g., "LLM", "SLM", "Model") to a unified set of tokens.
3.  **Update Logic:** When a file is patched, parse the new content, extract topics using a sliding window, and update the `co_occurrence_matrix` stored in `bag/index.json`.
4.  **Validation:** Add a check in `self_check()` to ensure `index.json` remains valid JSON.

## Risk
**Failure Mode:** The indexer might become a bottleneck or introduce a syntax error during the update process, causing `apply_patch_operations` to fail.
**Mitigation:** Wrap the index update in a `try-except` block. If the indexer fails, log the error and continue the patch (the index can be rebuilt later), ensuring the primary operation (the code patch) is never blocked by the secondary operation (the index update).

**Confidence Score:** 8/10