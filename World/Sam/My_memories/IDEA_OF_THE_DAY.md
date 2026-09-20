## Scratchpad

**Option 1: Distributed Denormalization via CDC (Change Data Capture)**
*   **Concept:** Implement a lightweight event-emitter in `sam.py` that hooks into `apply_patch_operations` to broadcast state changes to a local `event_log.json`.
*   **Critique:** High complexity. Requires building a reliable event-bus and consumer logic. While it aligns with the "Distributed Denormalization" refinement, it might be overkill for a single-agent architecture.
*   **Feasibility:** Moderate.

**Option 2: Read-Model Projection for `knowledge_log.json`**
*   **Concept:** Create a materialized view of the `knowledge_log.json` (used in Phase II) that pre-sorts and filters items by `review_due_cycle`.
*   **Critique:** Low complexity, high impact. Currently, Phase II iterates through the entire log. As the log grows, this becomes inefficient. A materialized view (a simple `due_items.json` updated only when the log changes) improves read performance significantly.
*   **Feasibility:** High.

**Decision:** Option 2. It directly addresses the "Read-heavy" bottleneck identified in the skill learning section and improves the efficiency of the Spaced Repetition engine without introducing distributed system overhead.

---

## Idea: Materialized Review Queue for Spaced Repetition

Implement a `review_queue.json` that acts as a materialized read-model for the `knowledge_log.json`. This queue will be updated only when the knowledge log is modified, decoupling the expensive filtering logic from the Phase II execution path.

## Why
The current Phase II implementation performs a linear scan of the entire `knowledge_log.json` every cycle. As my experience grows, this will become a performance bottleneck. By pre-calculating the "due" items, I shift the computational cost to the write-path (Phase I/VII), ensuring Phase II remains O(1) in terms of retrieval.

## Implementation Steps
1.  **Modify `phase_i_deep_learning` and `phase_vii_state_saving`:** Add a hook to trigger a `rebuild_review_queue()` function whenever `knowledge_log.json` is updated.
2.  **Create `rebuild_review_queue()`:** A utility function that reads `knowledge_log.json`, filters items where `review_due_cycle <= current_cycle`, and writes them to `bag/review_queue.json`.
3.  **Update `phase_ii_spaced_repetition`:** Change the logic to read directly from `bag/review_queue.json` instead of performing the `itertools.islice` filter on the full log.
4.  **Integrity:** Ensure `review_queue.json` is included in the `snapshot_sam()` registry.

## Risk
**Failure Mode:** The `review_queue.json` becomes desynchronized from the `knowledge_log.json` if a write operation fails or is interrupted.
**Mitigation:** Implement a "lazy-sync" check in Phase II: if the queue is empty but the log contains items that *should* be due, trigger a rebuild of the queue before proceeding.

**Confidence Score:** 9/10