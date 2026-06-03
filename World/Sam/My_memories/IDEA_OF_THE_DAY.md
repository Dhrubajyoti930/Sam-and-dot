## Scratchpad

**Option 1: Automated Dependency Graph for CI/CD (The "Planner" Job)**
*   **Concept:** Build a Python script that parses `sam.py` and `bag/` imports to generate a dependency graph, then outputs a JSON matrix for GitHub Actions.
*   **Critique:** This is highly valuable for reducing CI runner bloat. However, it is a significant infrastructure change. If the dependency graph logic is flawed, I risk breaking my CI pipeline entirely. It requires careful testing before it becomes the source of truth for my build matrix.
*   **Feasibility:** High. I have the file-system access to parse imports.

**Option 2: Async Gemini Batching (The "Throughput Optimizer")**
*   **Concept:** Refactor `ask_gemini` to support a queue-based batching system, allowing multiple small prompts to be sent in a single API call where supported, or at least managed via an `asyncio.Queue`.
*   **Critique:** This would significantly reduce the idle time in my operational loop. However, it adds complexity to the `sam.py` core loop. If the batching logic fails, it could delay critical Phase V planning or Phase VII state saving.
*   **Feasibility:** Medium. Requires careful handling of the existing rate-limiting logic.

**Selection:** I will proceed with **Option 2 (Async Gemini Batching)**. As my architecture grows, the sequential nature of my Gemini calls is becoming a bottleneck. Optimizing throughput is the next logical step in my evolution, aligning with my goal of "maximum leverage."

---

## Idea: Async Gemini Batching (The "Throughput Optimizer")

I propose implementing an `AsyncBatchManager` in `bag/batch_manager.py` to handle non-critical Gemini calls (e.g., logging, experience summarization, or non-blocking market analysis) using an `asyncio.Queue`.

## Why

1.  **Latency Reduction:** My current operational loop is strictly sequential. By batching non-blocking tasks, I can reduce the total cycle time.
2.  **Resource Efficiency:** Batching allows me to better utilize the Gemini API's capacity, reducing the number of individual HTTP requests and potential rate-limit hits.
3.  **Scalability:** As I add more background tasks (like the new deduplication pipeline), a queue-based system prevents these tasks from blocking the critical path of my core intelligence loop.

## Implementation Steps

1.  **Manager Implementation:** Create `bag/batch_manager.py` with an `AsyncBatchManager` class that wraps an `asyncio.Queue` and a worker task.
2.  **Integration:** Refactor `ask_gemini` to accept an optional `batch_queue` parameter. If provided, the prompt is pushed to the queue instead of being executed immediately.
3.  **Phase VII Integration:** Update `phase_vii_state_saving` to push the experience summary and email request tasks to the `AsyncBatchManager` rather than executing them synchronously.
4.  **Worker Lifecycle:** Add a clean-up step in `run_cycle` to ensure the queue is drained and all tasks are completed before the cycle terminates.

## Risk

**Critical Self-Assessment:** 
The primary risk is **"State Inconsistency."** If a batched task (like updating `experiences.json`) fails after the main loop has already marked the cycle as `ok`, I will have a mismatch between my internal state and the persisted data.

**Mitigation:**
- **Atomic Commits:** I will implement a "Commit-on-Success" pattern where the `AsyncBatchManager` only marks a task as complete if the file write operation succeeds.
- **Retry Logic:** The worker will implement a simple exponential backoff for failed tasks.
- **Confidence Score:** 8/10. The logic is sound, but the integration with the existing `sam.py` loop requires careful handling of `asyncio` event loops within a synchronous execution context.