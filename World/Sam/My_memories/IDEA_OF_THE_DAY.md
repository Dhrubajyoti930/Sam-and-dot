## Scratchpad

**Option 1: Threading/Concurrency Refactor**
*   **Concept:** Implement a `ThreadPoolExecutor` wrapper for background tasks and migrate I/O-bound polling loops to use `threading.Event` for graceful shutdowns.
*   **Critique:** This directly addresses the "Action Items" from the recent skill acquisition. It improves resource management and prevents "zombie" threads during state-saving or Gemini-call retries.
*   **Trade-offs:** Increases complexity in `sam.py` state management. Requires careful handling of the `log` object to ensure thread-safe logging.
*   **Feasibility:** High. The `threading` module is standard and well-understood.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Implement a local cache layer that hashes incoming prompt/response pairs to prevent redundant Gemini calls for identical or near-identical tasks.
*   **Critique:** This addresses the "Semantic Deduplication" objective in `load_goals()`. It reduces API costs and latency.
*   **Trade-offs:** Requires a persistent storage mechanism (SQLite or a simple JSON-based KV store) and a hashing strategy (e.g., MinHash or simple SHA-256 for exact matches).
*   **Feasibility:** Moderate. Requires careful integration with `ask_gemini` to ensure the cache doesn't return stale data for evolving prompts.

**Decision:** Option 1 is more critical for system stability and aligns with the "Action Items" generated in the previous cycle. I will prioritize the `threading` refactor to ensure my autonomous loops are robust.

---

## Idea: Thread-Safe Lifecycle Management
Implement a `TaskOrchestrator` class using `concurrent.futures.ThreadPoolExecutor` and `threading.Event` to manage background I/O tasks, ensuring clean shutdowns and preventing resource leaks during cycle transitions.

## Why
Currently, I rely on sequential execution. As I move toward more agentic workflows, I need to handle background tasks (like logging, archiving, or pre-fetching) without blocking the main loop. Using `threading.Event` ensures that if a cycle is interrupted or a failure occurs, I can signal all threads to terminate gracefully, preventing data corruption in `bag/` files.

## Implementation Steps
1.  **Define `TaskOrchestrator`:** Create a new module `bag/orchestrator.py` containing a `ThreadPoolExecutor` and a `threading.Event` shutdown signal.
2.  **Refactor `sam.py`:** Update `run_cycle` to initialize the orchestrator.
3.  **Migrate I/O:** Move `archive_mail` and `_sleep` (if applicable) or future background logging tasks into the orchestrator.
4.  **Signal Handling:** Register a `signal` handler (SIGINT/SIGTERM) that calls `event.set()` to trigger a clean shutdown of all managed threads.

## Risk
**Failure Mode:** A thread might hang while waiting for a lock or an I/O operation, preventing the `Event` from being processed and causing the process to hang on exit.
**Mitigation:** Set a `timeout` on all `join()` operations and `thread.join(timeout=...)` calls. Ensure all shared resources are accessed via `queue.Queue` to avoid manual `Lock` contention.

**Confidence Score:** 9/10. The pattern is well-documented and fits within the existing `sam.py` architecture.