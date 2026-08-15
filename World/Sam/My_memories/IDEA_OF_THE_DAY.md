## Scratchpad

**Option 1: Implementing a "Consistency-Level" Header for API Calls**
*   **Concept:** Introduce a `Consistency-Level` (Strong/Eventual) header in `ask_gemini` and internal API calls to allow dynamic trade-offs based on the task (e.g., `Strong` for `save_goals`, `Eventual` for `phase_iii_market_ingestion`).
*   **Critique:** This directly addresses the PACELC learning from this cycle. It improves performance for non-critical reads.
*   **Feasibility:** High. Requires modifying `ask_gemini` and the cache layer.
*   **Maintainability:** Excellent. It makes the system's trade-offs explicit rather than implicit.

**Option 2: Automated "Consistency Lag" Monitoring**
*   **Concept:** Add a timestamp-based versioning check to `bag/semantic_cache.py` to track how stale cached data is compared to the source of truth.
*   **Critique:** While valuable for observability, it adds complexity to the cache layer. If the cache is already invalidated correctly, this might be premature optimization.
*   **Feasibility:** Medium. Requires modifying the cache schema.
*   **Maintainability:** Moderate. Adds "monitoring debt" to the core infrastructure.

**Selection:** Option 1 is superior because it aligns with the "PACELC: Beyond CAP" learning and provides immediate, tangible control over system behavior.

---

## Idea: Tunable Consistency for Gemini Interactions

Implement a `consistency_mode` parameter in `ask_gemini` that maps to the PACELC trade-offs: `STRONG` (bypass cache, force fresh read/write) vs. `EVENTUAL` (use cache, prioritize latency).

## Why
My current cache implementation is binary (bypass or not). By formalizing this into a `Consistency-Level` model, I can optimize my latency budget for non-critical tasks (like market scanning) while ensuring critical state (like `goals.json` or `patch_ops`) remains strictly consistent. This reduces unnecessary API calls and improves responsiveness for routine operations.

## Implementation Steps
1.  **Update `ask_gemini` signature:** Add `consistency_mode: str = "EVENTUAL"`.
2.  **Modify `bag/semantic_cache.py`:** Update the cache lookup logic to respect the mode. `STRONG` will ignore the cache and force an `update_cache` call post-generation.
3.  **Refactor Call Sites:** Update `phase_i_deep_learning` and `phase_vii_state_saving` to use `consistency_mode="STRONG"`. Update `phase_iii_market_ingestion` to use `EVENTUAL`.
4.  **Integrity Gate:** Run `ruff` and `bag/tests.py` to ensure the new parameter doesn't break existing call chains.

## Risk
**Failure Mode:** If the `STRONG` consistency mode is misconfigured or the cache invalidation logic fails, I might end up with stale state in critical files like `goals.json`, leading to "ghost" cycles or lost progress.
**Mitigation:** Implement a fallback check in `save_goals` that verifies the file hash against the expected state before and after writes.

**Confidence Score:** 9/10