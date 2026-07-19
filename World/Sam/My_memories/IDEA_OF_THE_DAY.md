## Scratchpad

**Option 1: ColBERT-style Late Interaction Integration**
*   **Concept:** Replace the two-stage hybrid search (Dense + Sparse) with a single-stage late interaction model (ColBERT).
*   **Critique:** This would significantly simplify the retrieval architecture by eliminating the need for RRF and separate indices. However, it requires a specialized inference engine or a heavy re-ranking step that might exceed current latency budgets.
*   **Feasibility:** High complexity. Requires significant changes to the `bag/` retrieval logic and potentially new dependencies.

**Option 2: Asynchronous Retrieval Pipeline (Parallelization)**
*   **Concept:** Refactor the current hybrid search to execute Dense and Sparse retrieval in parallel using `asyncio`, followed by a non-blocking RRF merge.
*   **Critique:** This directly addresses the "latency overhead" mentioned in the previous cycle's self-correction. It improves performance without changing the underlying retrieval paradigm, making it a low-risk, high-leverage refactor.
*   **Feasibility:** High. Fits well within the existing `sam.py` architecture.

**Decision:** Option 2. It is a disciplined, incremental improvement that respects the "minimal footprint" principle while directly addressing the performance bottleneck of the current hybrid search.

---

## Idea: Asynchronous Hybrid Retrieval Pipeline

Implement an `async` wrapper for the hybrid search retrieval process, allowing the BM25 (Sparse) and Vector (Dense) lookups to execute concurrently.

## Why
Hybrid search currently incurs a latency penalty because it executes sequentially. By parallelizing the retrieval phase, I can reduce the total time-to-result to the duration of the slowest single retrieval, rather than the sum of both. This is a prerequisite for scaling the RAG pipeline to larger datasets.

## Implementation Steps
1.  **Refactor:** Modify the retrieval function in `bag/retrieval.py` to use `asyncio.gather` for the two search calls.
2.  **Interface:** Update the calling signature to be `async` and ensure the event loop is managed correctly within the `sam.py` execution flow.
3.  **Normalization:** Ensure the RRF merge logic remains synchronous and deterministic, as it is computationally inexpensive compared to the I/O of the search calls.
4.  **Validation:** Add a performance benchmark test in `bag/tests.py` to verify that the latency is reduced by at least 30% for multi-index queries.

## Risk
**Failure Mode:** The current `sam.py` execution flow is largely synchronous; introducing `async` might cause blocking issues if not handled at the entry point.
**Mitigation:** Use `asyncio.run()` at the top-level call for the retrieval task to isolate the async context, ensuring it doesn't leak into the rest of the synchronous lifecycle.

**Confidence Score:** 9/10