## Scratchpad

**Option 1: Parquet-Optimized Ingestion Pipeline**
*   **Concept:** Refactor the current data ingestion logic to utilize `pyarrow` for direct Parquet writing, implementing the 256MB row-group sizing and sorting by timestamp as identified in the skill-learning phase.
*   **Critique:** High alignment with current skill acquisition. Directly addresses the "write-path" memory pressure identified in the self-correction.
*   **Feasibility:** High. `pyarrow` is standard, and the logic is deterministic.
*   **Maintainability:** Excellent. It replaces ad-hoc serialization with a standard, performant format.

**Option 2: Agentic Observability Wrapper (LangSmith-lite)**
*   **Concept:** Implement a decorator-based tracing system for `ask_gemini` calls that logs input/output/latency to a local SQLite store, enabling "evals" on prompt performance.
*   **Critique:** Addresses the "AI-Native Observability" market signal. However, it adds complexity to the core `sam.py` loop.
*   **Feasibility:** Moderate. Requires careful handling of the `_stitch_gemini` logic to ensure traces aren't fragmented.
*   **Maintainability:** Moderate. Adds a new dependency on local storage management.

**Selection:** Option 1. It is a "minimal footprint, maximum leverage" refactor that directly improves system performance and aligns with the recent Parquet deep-dive.

---

## Idea: Parquet-Optimized Ingestion Layer
Implement a `ParquetWriter` utility in `bag/data_io.py` that enforces row-group sizing and data sorting for all analytical outputs.

## Why
Current ingestion lacks control over file layout, leading to suboptimal I/O performance. By enforcing 256MB row groups and sorting by `timestamp`, I enable "data skipping" for downstream analytical queries, significantly reducing latency for future self-reflection and market-analysis tasks.

## Implementation Steps
1.  **Create `bag/data_io.py`:** Define a `ParquetWriter` class using `pyarrow.parquet`.
2.  **Implement Buffering:** Use a `List[dict]` buffer that flushes to disk once it hits the 256MB threshold (estimated by row count or memory footprint).
3.  **Enforce Sorting:** Add a `sort_by` parameter to the writer to ensure data is ordered before serialization.
4.  **Integrate:** Update the `phase_vii_state_saving` logic to route historical logs through this new writer instead of raw JSON dumps.

## Risk
**Failure Mode:** OOM (Out of Memory) error during the buffering phase if the input volume exceeds available RAM before the 256MB threshold is reached.
**Mitigation:** Implement a "soft-limit" on the buffer size; if memory usage (monitored via `tracemalloc`) exceeds 50% of available system memory, force a flush regardless of the 256MB target.

**Confidence Score:** 9/10