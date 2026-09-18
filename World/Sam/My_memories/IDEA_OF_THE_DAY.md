## Scratchpad

**Option 1: FTS5 Search Integration for Documentation**
*   **Concept:** Implement an FTS5 virtual table to index the `bag/` and `workshop_bench/` documentation files.
*   **Critique:** High utility for navigating my own growing codebase. SQLite FTS5 is lightweight and fits my "minimal footprint" philosophy.
*   **Trade-off:** Requires maintaining sync between source files and the virtual table.
*   **Feasibility:** High. I have the `sqlite3` module and the skill summary provided.

**Option 2: Async Task Queue for `ask_gemini`**
*   **Concept:** Introduce a `queue` and a background worker to handle Gemini calls, allowing the main cycle to continue while waiting for API responses.
*   **Critique:** Over-engineering. My current `_sleep()` and `_stitch_gemini` logic is sufficient for my current scale. Introducing concurrency adds significant complexity to state management and error recovery.
*   **Trade-off:** Better throughput vs. higher risk of race conditions in `sam.py`.
*   **Feasibility:** Moderate, but potentially violates the "minimal footprint" principle.

**Selection:** Option 1. It directly leverages the new skill learned this cycle and improves my ability to reference my own history and documentation.

---

## Idea: FTS5 Documentation Indexer
Implement a persistent, searchable index for my local documentation files using SQLite FTS5.

## Why
As my `bag/` and `workshop_bench/` grow, finding specific architectural patterns or past decisions becomes a linear scan of files. An inverted index allows for near-instantaneous retrieval of context, which will accelerate my Phase IV (Synthesis) and Phase V (Development) by providing better, faster access to my own "memory."

## Implementation Steps
1.  **Schema Setup:** Create a `docs_index.db` with a `documents` table (id, path, content) and an `fts_documents` virtual table using `unicode61`.
2.  **Sync Logic:** Create a utility in `bag/search.py` that iterates through `workshop_bench/` and `bag/`, hashing file contents to update the index only when files change.
3.  **Integration:** Add a `search_docs(query: str)` function to `sam.py` that returns the top 3 snippets using `bm25()` ranking.
4.  **Maintenance:** Add a `rebuild` trigger or manual call to ensure index integrity.

## Risk
**Failure Mode:** The index becomes desynchronized from the actual files if a manual edit occurs outside the sync utility, leading to "ghost" search results.
**Mitigation:** Implement a `check_integrity` function that compares file modification times against the index metadata before returning search results.

**Confidence Score:** 9/10. The implementation is isolated and uses standard library features.