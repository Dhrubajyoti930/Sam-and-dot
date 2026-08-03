## Scratchpad

### Option 1: Observability of Replication Lag
*   **Concept:** Implement a heartbeat monitor between the primary `bag/` storage and a secondary "shadow" directory to measure latency in state propagation.
*   **Critique:** While this addresses the "eventual consistency" observability gap identified in my self-correction, it adds significant complexity to the `bag/` file system operations. It risks over-engineering for a local-first environment where network partitions are rare.
*   **Feasibility:** High, but potentially low value for the current single-node deployment.

### Option 2: Transactional Outbox for `MAIL_OUT`
*   **Concept:** Ensure that when I generate an `ALERT_*.md` or a `request.json`, the write is atomic and coupled with a "pending" flag in a local state file.
*   **Critique:** This directly addresses the "2PC vs Eventual Consistency" learning. It ensures that Dot never sees a partial or corrupted communication file. It aligns with the "Transactional Outbox" pattern I studied.
*   **Feasibility:** Very high. It leverages existing `bag/patch_ops` logic and improves the reliability of my communication channel with Dot.

**Decision:** Option 2. It is a concrete application of my recent learning, improves system reliability, and respects the "minimal footprint" constraint.

---

## Idea: Transactional Outbox for External Communication

Implement a `TransactionalOutbox` class in `bag/outbox.py` to manage the lifecycle of `MAIL_OUT` and `request.json` files. Instead of writing directly to `MAIL_OUT`, I will write to a `pending/` directory and move the file to `MAIL_OUT` only after a successful metadata commit.

## Why
My current communication method is susceptible to partial writes if the process is interrupted. By implementing a transactional outbox, I ensure that Dot only ever interacts with complete, verified files, adhering to the ACID principles I explored in my recent study.

## Implementation Steps
1.  **Create `bag/outbox.py`:** Define `TransactionalOutbox` with `stage(filename, content)` and `commit(filename)` methods.
2.  **Update `_alert_dot`:** Refactor to use `outbox.stage()` and `outbox.commit()` instead of direct `Path.write_text()`.
3.  **Update `maybe_write_email_request`:** Integrate the outbox pattern for `request.json` to ensure the request is fully formed before it becomes visible to the system.
4.  **Integrate Cleanup:** Add a `purge_staged()` method to clear abandoned files from the `pending/` directory during `run_cycle` initialization.

## Risk
**Failure Mode:** The `commit` operation (a file move) could fail due to filesystem permissions or disk space, leaving a "staged" file that is never sent.
**Mitigation:** Add a `check_staged()` method in `run_cycle` that logs a warning if files remain in `pending/` for more than one cycle, allowing me to manually intervene or retry.

**Confidence Score:** 9/10