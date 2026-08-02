## Scratchpad

**Option 1: Event-Sourced State Manager**
*   **Concept:** Replace the current `load_goals` / `save_goals` JSON-overwrite pattern with an append-only `events.log` and a `State` projection.
*   **Critique:** 
    *   *Pros:* Provides a perfect audit trail of every cycle's evolution; aligns with the "Event Sourcing" skill learned this cycle.
    *   *Cons:* High complexity for a simple `goals.json` file. Requires building a robust "Upcaster" for schema evolution if the goal structure changes.
    *   *Feasibility:* High, given the existing `bag/` infrastructure.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Implement a vector-based check in `phase_iv_synthesis` to compare the current `idea` against `experiences.json` to prevent redundant development.
*   **Critique:**
    *   *Pros:* Directly addresses the "Sam is not a yes-machine" trait; ensures forward momentum by filtering out "re-inventing the wheel" ideas.
    *   *Cons:* Requires a local embedding model (e.g., `sentence-transformers`) which adds a dependency.
    *   *Feasibility:* Medium.

**Selection:** Option 1. It is a foundational architectural shift that directly applies the "Event Sourcing" skill and improves the integrity of my self-improvement tracking.

---

## Idea: Event-Sourced Goal Management
Transition `goals.json` from a state-based file to an append-only `goals_event_store.jsonl` where each line is an immutable event (e.g., `CycleStarted`, `MetricLogged`, `ObjectiveCompleted`).

## Why
Current state-saving is prone to corruption if a process is interrupted. An event-sourced approach ensures that even if a write fails, the history remains intact. It allows me to "replay" my growth history to generate more accurate 1% metrics and provides a clear audit trail for Dot.

## Implementation Steps
1.  **Define Schema:** Create a Pydantic model for `GoalEvent` (timestamp, event_type, payload).
2.  **Interface:** Implement `append_event(event: GoalEvent)` in `sam.py`.
3.  **Projection:** Create `get_current_state()` which folds the event log into the current `goals` dictionary.
4.  **Snapshotting:** Implement a `snapshot_goals()` function that writes the current state to `goals_snapshot.json` every 10 cycles to keep replay time low.

## Risk
**Failure Mode:** The projection logic becomes desynchronized from the event log due to a bug in the folding function.
**Mitigation:** Implement a `verify_integrity()` check that compares the projected state against a hash of the event log.
**Confidence Score:** 8/10. The logic is straightforward, but the transition requires careful migration of the existing `goals.json` data.