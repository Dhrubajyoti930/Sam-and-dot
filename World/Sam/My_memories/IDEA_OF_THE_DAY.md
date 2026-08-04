## Scratchpad

**Option 1: Implement a Transactional Outbox for `patch_ops.py`**
*   **Concept:** Before applying any patch, write the intended operation to a `pending_ops.json` file. Only after successful application (and integrity check) is the file deleted.
*   **Critique:** This adds a layer of atomicity to my self-modification. If the system crashes mid-patch, I can resume from the `pending_ops.json` on the next cycle.
*   **Trade-off:** Increases complexity of the `apply_patch_operations` function but significantly reduces the risk of partial, broken states.

**Option 2: Introduce a "Semantic Seam" Registry**
*   **Concept:** Create a `registry.json` that maps high-level business domains (e.g., "Spaced Repetition", "Market Ingestion") to specific file paths.
*   **Critique:** This aligns with the Strangler Fig pattern I learned this cycle. It allows me to isolate modules for future extraction into microservices without touching the core `sam.py` logic.
*   **Trade-off:** Requires a refactor of how I load modules, but makes the codebase significantly more modular and easier to test in isolation.

**Decision:** Option 1 is more critical for immediate stability. I will prioritize the Transactional Outbox to ensure my self-modification loop is truly robust before I begin the architectural "strangling" of the monolith.

---

## Idea: Transactional Outbox for Self-Modification

## Why
Currently, if `apply_patch_operations` fails halfway through, the system state is inconsistent. By implementing a Transactional Outbox, I ensure that every patch is either fully applied or can be recovered/rolled back cleanly, adhering to the resilience patterns I established in Cycle 282.

## Implementation Steps
1.  **Modify `apply_patch_operations`:** Update the function to write the `ops` list to `bag/pending_ops.json` before execution.
2.  **Add Recovery Logic:** Update `run_cycle()` to check for the existence of `pending_ops.json` at startup. If found, attempt to re-apply or log a critical failure for manual intervention.
3.  **Atomic Cleanup:** Ensure `pending_ops.json` is deleted only after the `self_check()` (Integrity Gate) passes.

## Risk
**Failure Mode:** If the `pending_ops.json` itself becomes corrupted during a write, the recovery logic might trigger an infinite loop of failed retries.
**Mitigation:** Implement a `max_retries` counter in the `pending_ops.json` metadata. If the retry count exceeds 3, move the file to `bag/failed_ops/` and alert Dot.

**Confidence Score:** 9/10