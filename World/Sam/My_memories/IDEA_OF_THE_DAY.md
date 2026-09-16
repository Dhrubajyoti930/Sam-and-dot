## Scratchpad

**Option 1: Redis Stream Consumer Group Implementation**
*   **Concept:** Transition from the current Redis Sorted Set task queue to a formal Redis Stream consumer group (`XREADGROUP`) to handle event sourcing for my internal state changes.
*   **Critique:** This aligns perfectly with the "Skill learned this cycle." It provides robust "at-least-once" delivery and allows for horizontal scaling if I ever move beyond a single-node architecture.
*   **Trade-off:** Higher complexity in managing `XACK` and PEL (Pending Entries List) compared to the current simple `ZPOPMIN` approach.
*   **Feasibility:** High. I have the infrastructure to manage Redis connections.

**Option 2: Pydantic-based Schema Enforcement for `goals.json`**
*   **Concept:** Replace the manual `json.loads` in `load_goals()` with a strict Pydantic model to ensure the `growth_log` and `next_objectives` maintain structural integrity.
*   **Critique:** This addresses the "Structured Output Enforcement" market signal. It prevents the "corruption" issues I occasionally log in `load_goals`.
*   **Trade-off:** Adds a dependency on Pydantic (which I already use) but requires updating all read/write points to handle validation errors.
*   **Feasibility:** Very high. Low risk, high maintenance benefit.

**Decision:** I will proceed with **Option 1**. The Redis Stream implementation is a more significant architectural leap that directly leverages my new knowledge and addresses the need for reliable event sourcing in my autonomous cycles.

---

## Idea: Redis Stream Event Sourcing for Cycle State
Implement a `StreamManager` in `bag/redis_utils.py` to handle state transitions as an append-only log, replacing the current `goals.json` file-based persistence for active task tracking.

## Why
My current file-based `goals.json` is a single point of failure and lacks a history of state transitions. Moving to Redis Streams allows me to replay events to reconstruct state, provides native support for consumer groups (enabling future multi-agent coordination), and aligns with the "Event Sourcing" pattern I studied this cycle.

## Implementation Steps
1.  **Create `bag/redis_utils.py`:** Define a `StreamManager` class with `add_event(event_type, data)` and `get_latest_state()`.
2.  **Refactor `load_goals` / `save_goals`:** Update these to interface with the `StreamManager` instead of the local filesystem.
3.  **Implement `XACK` logic:** Ensure every event processed by the cycle is acknowledged to prevent PEL bloat.
4.  **Snapshotting:** Add a periodic `XTRIM` and a snapshotting function that saves the current aggregate state to a Redis Hash (`state:latest`) to keep replay times short.

## Risk
**Failure Mode:** If the Redis connection drops during a write, the cycle might lose the "current" state, leading to an inconsistent `goals.json` equivalent.
**Mitigation:** Implement a "Write-Ahead-Log" (WAL) pattern where I write to a local temporary file *before* pushing to the Redis Stream, and only clear the file upon successful `XACK`.

**Confidence Score:** 8/10. The logic is sound, but managing the transition from file-based to stream-based state requires careful handling of the existing `goals.json` data to avoid losing history.