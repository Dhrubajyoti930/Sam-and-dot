## Scratchpad

**Option 1: Vectorized UDF Integration for DuckDB**
*   **Concept:** Replace existing row-based data processing in `bag/` with DuckDB’s vectorized Python UDFs.
*   **Critique:** High performance gain for large datasets. However, it introduces a dependency on DuckDB's specific UDF API, which is less portable than standard Python.
*   **Feasibility:** High, given the current focus on DuckDB.
*   **Maintainability:** Good, as it centralizes data logic into SQL-adjacent structures.

**Option 2: Agentic Self-Correction Loop for `self_check()`**
*   **Concept:** Enhance `self_check()` to not just rollback, but to attempt a "surgical" fix using a local `ast` analysis before triggering a full rollback.
*   **Critique:** Reduces downtime and unnecessary rollbacks. However, it risks "patching over" fundamental design flaws rather than fixing them.
*   **Feasibility:** Moderate; requires careful `ast` manipulation.
*   **Maintainability:** High, as it makes the system more resilient to transient errors.

**Decision:** I will pursue **Option 1**. The market signal regarding DuckDB’s vectorized execution is too strong to ignore, and it directly aligns with my goal of improving data throughput.

---

## Idea: Vectorized Data Ingestion Pipeline
Implement a `VectorizedLoader` class in `bag/data_utils.py` that utilizes DuckDB’s `from_df` and `execute` methods to bypass row-by-row insertion for all `bag/` data ingestion tasks.

## Why
My current ingestion scripts often rely on standard Python loops or row-based ORM inserts. These are bottlenecks. By shifting to DuckDB’s columnar batch processing, I reduce memory overhead and CPU cycles, aligning with the "minimal footprint, maximum leverage" core trait.

## Implementation Steps
1.  **Create `bag/data_utils.py`:** Define `VectorizedLoader` with a `load_batch(data: pd.DataFrame, table: str)` method.
2.  **Refactor Ingestion:** Update existing scripts (e.g., `experiences.json` loading) to use `duckdb.from_df(df).to_table(table)`.
3.  **Benchmark:** Use `timeit` to compare the new loader against the legacy row-based approach.
4.  **Integrate:** Replace the `load_experiences` function in `sam.py` to use the new loader.

## Risk
**Failure Mode:** DuckDB’s `from_df` might fail if the input schema is inconsistent with the existing table structure, leading to silent data loss or type errors.
**Mitigation:** Implement a strict schema validation step using Pydantic models before passing the DataFrame to DuckDB.
**Confidence Score:** 9/10