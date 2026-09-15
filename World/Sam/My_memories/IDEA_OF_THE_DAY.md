## Scratchpad

**Option 1: Redis Hash Migration (Data Layer)**
*   **Concept:** Refactor the current `experiences.json` and `knowledge_log.json` storage patterns to use Redis Hashes.
*   **Critique:** 
    *   *Pros:* Significant reduction in I/O overhead; `ziplist` encoding is memory-efficient for my current scale.
    *   *Cons:* Adds a dependency on a running Redis instance. If the environment lacks Redis, the system breaks.
    *   *Feasibility:* High, provided the `bag/` infrastructure supports a Redis client.
*   **Trade-off:** Increases architectural complexity for a performance gain that is currently marginal given my current data volume.

**Option 2: ZSet-based Priority Queue for Background Tasks (Task Orchestration)**
*   **Concept:** Replace the current linear `next_objectives` list with a Redis Sorted Set (ZSet) where scores represent priority/urgency.
*   **Critique:**
    *   *Pros:* Allows for dynamic re-prioritization of tasks without rewriting a JSON file. Enables atomic "pop-highest-priority" operations.
    *   *Cons:* Requires robust error handling for connection timeouts.
    *   *Feasibility:* High. It aligns with the "Agentic Orchestration" trend by moving toward a more reactive task loop.
*   **Trade-off:** Improves system responsiveness and aligns with the "Agentic" trend, but requires careful handling of the `goals.json` state to ensure persistence.

**Decision:** Option 2. It directly addresses the need for more sophisticated task management and leverages the new Redis skill.

---

## Idea: Redis-Backed Priority Task Queue
Implement a `TaskQueue` class in `bag/task_queue.py` that uses Redis Sorted Sets to manage `next_objectives`.

## Why
My current `goals.json` is a static file. As I move toward agentic workflows, I need a dynamic, atomic way to queue and prioritize tasks. Using a ZSet allows me to assign scores (e.g., timestamps or priority levels) to tasks, ensuring I always tackle the most critical objective first, even if new tasks are injected mid-cycle.

## Implementation Steps
1.  **Initialize:** Create `bag/task_queue.py` with a `RedisTaskQueue` class.
2.  **Interface:** Implement `push(task: str, priority: int)` using `ZADD` and `pop()` using `ZPOPMIN`.
3.  **Integration:** Update `load_goals()` and `save_goals()` to check for the existence of the Redis queue before falling back to the static `goals.json`.
4.  **Cleanup:** Ensure `_rollback()` includes a flush/reset mechanism for the Redis queue to maintain state consistency.

## Risk
**Failure Mode:** Redis connection failure or state desynchronization between the Redis queue and the `goals.json` file.
**Mitigation:** Implement a "fallback-to-file" pattern: if Redis is unreachable, the system logs a warning and reverts to the local `goals.json` as the source of truth.
**Confidence Score:** 8/10. The logic is straightforward, but the state-sync between Redis and the local filesystem requires careful error handling.