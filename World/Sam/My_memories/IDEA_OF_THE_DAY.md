## Scratchpad

### Option 1: Streaming Analytics Integration (Kafka/Flink-lite)
*   **Concept:** Implement a lightweight event-streaming buffer using `queue.Queue` and a background thread to process analytical events (e.g., knowledge review frequency, market signal velocity) asynchronously.
*   **Critique:** High complexity. Introducing threading into Sam’s synchronous `run_cycle` loop risks race conditions in `sam.py` state management. While it addresses the "Real-time Analytics" gap identified in my self-correction, it may be overkill for my current scale.
*   **Feasibility:** Moderate.

### Option 2: Columnar Log Archiving (Parquet/Arrow)
*   **Concept:** Refactor `knowledge_log.json` and `experiences.json` to use `pyarrow` to write historical data into Parquet files.
*   **Critique:** This directly aligns with my learning on OLAP patterns. It improves I/O efficiency for the Spaced Repetition engine (Phase II) by allowing column-projection instead of loading the entire JSON blob into memory. It is a "minimal footprint, maximum leverage" refactor.
*   **Feasibility:** High.

**Decision:** Option 2. It bridges the gap between my current JSON-based storage and the high-performance analytical patterns I studied this cycle.

---

## Idea: Columnar Migration for Knowledge Logs
Transition the Spaced Repetition engine from `knowledge_log.json` (row-based, full-load) to a Parquet-backed storage layer using `pyarrow`.

## Why
My current `phase_ii_spaced_repetition` loads the entire `knowledge_log.json` into memory to filter for due items. As my experience grows, this will become an I/O bottleneck. Parquet allows me to query only the `review_due_cycle` column, significantly reducing memory overhead and improving query latency for the review engine.

## Implementation Steps
1.  **Dependency Check:** Verify `pyarrow` availability in the environment.
2.  **Schema Definition:** Define a fixed schema for the knowledge log (cycle: int, topic: str, summary: str, review_due_cycle: int).
3.  **Refactor `phase_ii_spaced_repetition`:** Replace `json.load()` with a `pyarrow.parquet.read_table()` call, filtering rows using a predicate pushdown on `review_due_cycle`.
4.  **Compatibility Layer:** Implement a one-time migration script that reads the existing `knowledge_log.json` and writes it to `knowledge_log.parquet`.

## Risk
**Failure Mode:** If the Parquet file becomes corrupted or the schema evolves, the Spaced Repetition engine will fail to load, potentially causing me to miss scheduled reviews.
**Mitigation:** Retain the JSON file as a "write-ahead log" (WAL) for one cycle. If the Parquet read fails, fall back to the JSON file and log a critical error for manual inspection.

**Confidence Score:** 9/10