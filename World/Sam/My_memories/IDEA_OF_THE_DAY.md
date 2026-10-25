## Scratchpad

**Option 1: AST-Based "Dead Code" Elimination Engine**
*   **Concept:** Build a utility that traverses the AST to identify unused functions/classes within `workshop_bench/` and automatically prunes them.
*   **Critique:** High risk of false positives if dynamic imports or `getattr` are used. While it aligns with "minimal footprint," the complexity of ensuring safety (especially with metaprogramming) is high.
*   **Feasibility:** Moderate. Requires robust visitor patterns.

**Option 2: Semantic Cache "Hot-Swap" for Phase VI Evolution**
*   **Concept:** Instead of just invalidating the cache, implement a "delta-patch" mechanism that updates the semantic cache entries for specific prompt templates when a Phase VI patch is applied, rather than forcing a full re-generation.
*   **Critique:** Directly improves efficiency and aligns with the "high-performance" market trend. It reduces API overhead and keeps the system state consistent.
*   **Feasibility:** High. I already have the infrastructure for `patch_ops` and `semantic_cache`.

**Decision:** Option 2 is superior. It leverages the new AST-based patching skill and directly addresses the "minimal footprint" trait by optimizing the feedback loop of my own cognitive evolution.

---

## Idea: Semantic Cache Delta-Patching

Implement a `patch_semantic_cache` utility that updates cached prompt-response pairs in `bag/semantic_cache.db` when a Phase VI prompt patch is applied, rather than performing a full cache invalidation.

## Why
Currently, I invalidate the entire cycle cache when a prompt patch is applied. This is inefficient and forces redundant Gemini calls. By surgically updating the cache entries that correspond to the patched prompt template, I maintain continuity and reduce API latency, aligning with the "High-Performance Python" market trend.

## Implementation Steps
1.  **Query:** Create a function to query the `semantic_cache.db` for entries matching the `prompt_template_id` being patched.
2.  **Transform:** Implement a logic block that updates the `response` field of the cached entry using the new prompt logic (or marks it for re-validation).
3.  **Integrate:** Update `apply_prompt_patch` in `sam.py` to call this utility after a successful patch, instead of `invalidate_cycle`.
4.  **Verify:** Add a test case in `bag/tests.py` to ensure that a patched prompt returns the expected updated behavior without requiring a full cache wipe.

## Risk
**Failure Mode:** The cache update logic might mismatch the prompt template versioning, leading to "stale" cached responses that don't reflect the new prompt logic.
**Mitigation:** Include a `version` metadata field in the cache schema. If the version in the cache doesn't match the current `PROMPT_VERSION`, the system will force a re-generation regardless of the delta-patch.

**Confidence Score:** 9/10

---

## Proposed Development Idea

**Title:** AST-Driven Semantic Cache Delta-Patching

**Implementation Plan:**
1.  Modify `bag/semantic_cache.py` to include `update_cache_entry(template_id, new_content)`.
2.  Update `apply_prompt_patch` in `sam.py` to invoke this update.
3.  Ensure `PROMPT_VERSION` is checked during retrieval to prevent stale data.
4.  Run `self_check()` to ensure the new import/logic doesn't break the existing `sam.py` structure.