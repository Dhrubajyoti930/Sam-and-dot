## Scratchpad

**Option 1: Implement a "Lazy-Loading" Semantic Cache**
*   **Concept:** Currently, `ask_gemini` checks the cache at the start of every call. I could refactor the cache to be a lazy-loaded proxy that only initializes the database connection if a cache hit is not found in a memory-resident bloom filter.
*   **Critique:** This reduces I/O latency for cache misses. However, it adds complexity to the `ask_gemini` flow. The current bottleneck is the network request to Gemini, not the SQLite cache lookup.
*   **Feasibility:** High.
*   **Maintainability:** Moderate; adds a layer of indirection.

**Option 2: Integrate Polars for `knowledge_log.json` Analysis**
*   **Concept:** Replace the current `itertools.islice` logic in `phase_ii_spaced_repetition` with a Polars-based query. This would allow for more complex scheduling logic (e.g., weighted random sampling based on "forgetting curves" or difficulty scores) without loading the entire JSON into memory.
*   **Critique:** This aligns perfectly with the "Skill learned this cycle" (Polars). It moves away from imperative list iteration to a declarative query plan. It is highly maintainable and scales better as the `knowledge_log` grows.
*   **Feasibility:** High.
*   **Maintainability:** High; cleaner, more robust code.

**Decision:** Option 2. It directly applies the new skill, improves the Spaced Repetition engine, and replaces inefficient list-based filtering with a performant, lazy-evaluated query.

---

## Idea: Polars-Powered Spaced Repetition Engine

Refactor `phase_ii_spaced_repetition` to use Polars for selecting knowledge items due for review.

## Why
The current implementation uses `itertools.islice` on a list loaded into memory. As my `knowledge_log.json` grows, this becomes inefficient. Polars allows me to treat the knowledge log as a lazy DataFrame, enabling predicate pushdown and efficient filtering. This is a practical application of the "Polars vs. Pandas" lesson, demonstrating a shift toward memory-efficient, declarative data processing.

## Implementation Steps
1.  **Dependency Check:** Ensure `polars` is available in the environment.
2.  **Refactor `phase_ii_spaced_repetition`:**
    *   Load `knowledge_log.json` directly into a Polars `LazyFrame` using `pl.scan_ndjson` or `pl.read_json`.
    *   Define a filter expression: `pl.col("review_due_cycle") <= cycle_num`.
    *   Use `.collect()` to retrieve only the required rows.
    *   Update the `review_due_cycle` values using Polars' `with_columns` and write back to JSON.
3.  **Validation:** Run `bag/tests.py` to ensure the scheduling logic remains consistent with previous cycles.

## Risk
**Failure Mode:** The `knowledge_log.json` schema might be inconsistent or contain malformed entries that cause Polars' strict schema inference to fail.
**Mitigation:** Use `pl.read_json` with explicit schema definition or a `try-except` block that falls back to the legacy list-based approach if the DataFrame construction fails, ensuring system stability.

**Confidence Score:** 9/10