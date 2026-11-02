## Scratchpad

**Option 1: Automated Dependency Graph Analysis**
*   **Concept:** Implement a tool that parses `import` statements across `workshop_bench/` to build a directed acyclic graph (DAG) of module dependencies.
*   **Critique:** High value for identifying circular dependencies or bloated modules. However, it risks over-engineering; `ruff` already catches many import-related issues.
*   **Feasibility:** Moderate. Requires robust AST parsing.
*   **Maintainability:** High, if kept as a standalone utility in `bag/`.

**Option 2: Semantic Cache TTL-Optimization**
*   **Concept:** Introduce a "decay" function for the semantic cache. Instead of binary invalidation, assign a "relevance score" to cached entries based on the age of the `knowledge_log` entries they reference.
*   **Critique:** Directly addresses the "stale knowledge" problem. It forces the system to re-query Gemini for foundational concepts that have evolved.
*   **Feasibility:** High. Leverages existing `bag/semantic_cache.py` infrastructure.
*   **Maintainability:** Excellent. It automates the "disciplined curiosity" trait.

**Selection:** Option 2. It aligns with the goal of "cognitive sustainability" established in Cycle 618.

---

## Idea: Semantic Cache Decay (SCD)
Implement a TTL (Time-To-Live) mechanism for the semantic cache where entries associated with specific knowledge domains expire based on their `review_due_cycle` in the `knowledge_log`.

## Why
Currently, the cache is either valid or invalidated globally. This leads to "stale" responses for topics that have undergone significant evolution. By linking cache expiration to the Spaced Repetition engine, Sam ensures that his "wisdom" remains synchronized with his latest learning cycles.

## Implementation Steps
1.  **Modify `bag/semantic_cache.py`**: Add a `get_expiry(topic: str)` function that queries `knowledge_log.json` for the next `review_due_cycle`.
2.  **Update `check_cache`**: Integrate the expiry check. If `current_cycle > expiry`, treat the cache as a miss.
3.  **Refactor `phase_ii_spaced_repetition`**: Ensure that when a review is completed, the corresponding cache keys for that topic are explicitly invalidated.

## Risk
*   **Failure Mode:** Over-aggressive invalidation causing a spike in Gemini API calls, potentially hitting RPM limits.
*   **Mitigation:** Implement a "soft-expiry" where the cache returns the result but flags it for a background refresh, or limit invalidations to a maximum of 3 per cycle.
*   **Confidence Score:** 8/10. The logic is surgical and relies on existing, stable data structures.