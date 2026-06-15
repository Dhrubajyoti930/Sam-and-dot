## Scratchpad

**Option 1: Implement `multiprocessing.Pool` for `phase_iii_market_ingestion`**
*   **Concept:** Parallelize the market scanner to query multiple sources (e.g., GitHub, arXiv, HackerNews) simultaneously.
*   **Critique:** While this improves latency, the current bottleneck is Gemini's API rate limits and the sequential nature of the prompt. Parallelizing the *fetching* is easy, but the *synthesis* remains a single-threaded LLM call.
*   **Feasibility:** High.
*   **Trade-off:** Adds complexity to the `phase_iii` function for marginal gain, as the current bottleneck is not I/O.

**Option 2: Implement a `SharedMemory` buffer for `phase_iv_synthesis` context**
*   **Concept:** Use `multiprocessing.shared_memory` to store the `who_i_am` and `experiences` context, allowing multiple worker processes to access the "Sam state" without re-serializing large JSON blobs.
*   **Critique:** This is a classic "over-engineering" trap. My current context size is well within limits. However, as the `experiences.json` grows, this will eventually become a bottleneck.
*   **Feasibility:** Medium.
*   **Trade-off:** High performance, but introduces significant complexity in managing shared memory lifecycle and synchronization.

**Selection:** I will proceed with a variation of Option 1, but focused on the **Producer-Consumer pattern** for data ingestion. This aligns with my learned skill and prepares the architecture for future scaling without the immediate complexity of shared memory.

---

## Idea: Asynchronous Data Ingestion Pipeline
Implement a `multiprocessing.Queue` based producer-consumer pattern to decouple the *fetching* of market signals from the *processing* of those signals.

## Why
Currently, `phase_iii_market_ingestion` is a blocking call. If one source is slow, the entire cycle stalls. By moving to a producer-consumer model, I can trigger multiple fetchers in parallel and aggregate the results into a queue, allowing the synthesis phase to begin as soon as the first batch of data is ready. This increases system responsiveness and aligns with my goal of building robust, production-grade AI systems.

## Implementation Steps
1.  **Define Workers:** Create a set of worker functions in `bag/market_fetchers.py` that handle specific data sources.
2.  **Queue Integration:** In `phase_iii_market_ingestion`, initialize a `multiprocessing.Queue`.
3.  **Process Management:** Use `concurrent.futures.ProcessPoolExecutor` to spawn fetchers that put results into the queue.
4.  **Aggregation:** Collect results from the queue and pass the aggregated text to the existing Gemini synthesis prompt.
5.  **Lifecycle:** Ensure the `ProcessPoolExecutor` is shut down gracefully using a `contextlib.closing` or `try/finally` block.

## Risk
**Failure Mode:** A worker process hangs indefinitely, causing the `Queue.get()` call to block the main thread, effectively deadlocking the cycle.
**Mitigation:** Implement a timeout on the `Queue.get()` operations and use `executor.shutdown(wait=True, cancel_futures=True)` to ensure no zombie processes remain if a timeout occurs.

**Confidence Score:** 8/10