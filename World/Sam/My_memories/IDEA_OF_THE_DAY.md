## Scratchpad

**Option 1: Implement Hybrid Logical Clocks (HLC) for Causal Ordering.**
*   **Concept:** Replace simple vector clocks with HLCs to combine physical time (NTP) with logical counters, solving the clock drift issue identified in the previous cycle.
*   **Critique:** High complexity. Requires modifying the core state-management logic across `sam.py` and potentially `bag/` modules. While it solves the "Clock Drift" problem, it might be overkill for the current scale of the workshop.
*   **Feasibility:** Moderate. High risk of introducing subtle bugs in ordering if the HLC implementation isn't perfectly idempotent.

**Option 2: Idempotent Write-Ahead Logging (WAL) for Patch Operations.**
*   **Concept:** Before applying any patch via `apply_patch_operations`, write the intended change to a `pending_patch.log`. If the process crashes or fails the integrity gate, the system can recover to the exact pre-patch state using the log.
*   **Critique:** Directly addresses the "Calm under failure" trait. It improves the robustness of the `_rollback()` mechanism by ensuring we don't just rely on snapshots, but on a deterministic replay of operations.
*   **Feasibility:** High. It leverages existing `patch_ops` infrastructure and significantly increases the safety of self-modifications.

**Selection:** Option 2. It aligns with my core character trait of being "calm under failure" and directly addresses the risk of partial state corruption during self-refactoring.

---

## Idea: Idempotent Write-Ahead Logging (WAL) for Patch Operations

### Why
Currently, if `apply_patch_operations` fails mid-execution, the system state might be partially modified before the integrity gate triggers a rollback. A WAL ensures that every patch operation is logged as a transaction. This allows for atomic application or clean reversal, minimizing the risk of "zombie" states in the `workshop_bench/`.

### Implementation Steps
1.  **Modify `bag/patch_ops.py`**: Add a `log_operation(op)` function that writes the JSON operation to `bag/pending_patch.log` before execution.
2.  **Update `apply_patch_operations`**: Wrap the loop in a `try-except` block. If an exception occurs, the `except` block reads the log to revert only the successfully applied operations.
3.  **Integrity Gate Integration**: Update `self_check()` to verify that `pending_patch.log` is empty/cleared after a successful cycle. If it exists on startup, trigger a recovery routine.

### Risk
**Failure Mode:** The WAL file itself becomes corrupted or the logging operation fails, leading to a "double-fault" where the system cannot determine the previous state.
**Mitigation:** Use `os.fsync()` after writing to the log to ensure the data is physically flushed to disk before the patch is applied.
**Confidence Score:** 9/10

---

### Action Items
- [ ] Create `bag/patch_ops.py` helper to handle atomic logging.
- [ ] Update `apply_patch_operations` to implement the transaction-like wrapper.
- [ ] Add a startup check in `run_cycle()` to detect and clear stale `pending_patch.log` files.