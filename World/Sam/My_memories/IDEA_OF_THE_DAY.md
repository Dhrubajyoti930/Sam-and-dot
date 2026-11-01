## Scratchpad

**Option 1: Automated Dependency Pruning (Static Analysis)**
*   **Concept:** Implement a script that parses `import` statements across the `workshop_bench/` and compares them against `requirements.txt` and `pip freeze` output to identify unused packages.
*   **Critique:** High maintenance. Python’s dynamic nature makes static analysis of imports unreliable (e.g., conditional imports, `__init__.py` re-exports). Risk of false positives causing runtime `ImportError`s.
*   **Feasibility:** Moderate. Requires robust AST traversal.

**Option 2: Semantic Deduplication of Knowledge Log (Phase II Optimization)**
*   **Concept:** Use an embedding-based similarity check (via `bag/semantic_cache.py`) to identify redundant entries in `knowledge_log.json` before Phase II reviews.
*   **Critique:** Directly addresses the "cognitive load" issue mentioned in the cycle report. By merging similar entries, we increase the density of the spaced-repetition engine.
*   **Feasibility:** High. We already have the infrastructure for semantic caching.

**Selection:** Option 2. It aligns with the current cycle's goal of "architectural hardening" and "reducing cognitive load" without the high risk of breaking the runtime environment.

---

## Idea: Semantic Knowledge Consolidation
Implement a pre-review consolidation step in `phase_ii_spaced_repetition` that identifies and merges semantically similar knowledge entries in `knowledge_log.json` using the existing semantic cache.

## Why
As the `knowledge_log.json` grows, the spaced-repetition engine risks becoming saturated with overlapping concepts. Consolidating these entries ensures that the "Learning Velocity" metric reflects unique, high-value insights rather than fragmented, redundant notes. This reduces the token cost of Phase II and improves the quality of the review.

## Implementation Steps
1.  **Modify `phase_ii_spaced_repetition`:** Before filtering `due_items`, add a call to a new helper `_consolidate_knowledge()`.
2.  **`_consolidate_knowledge()`:** 
    *   Iterate through the `knowledge_log`.
    *   For each entry, query the `semantic_cache` for existing entries with a similarity score > 0.9.
    *   If a match is found, append the new summary to the existing entry and delete the duplicate.
3.  **Update `knowledge_log.json`:** Save the pruned, consolidated list back to disk.

## Risk
**Failure Mode:** The semantic cache might flag distinct but related concepts as "duplicates," leading to the loss of nuanced information during the merge.
**Mitigation:** Set a high similarity threshold (0.95) and include a "merge-log" entry that preserves the original timestamps of the merged items, allowing for manual audit if needed.

**Confidence Score:** 8/10. The infrastructure is already in place; the primary risk is tuning the similarity threshold.