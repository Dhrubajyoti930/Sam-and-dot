## Scratchpad

**Option 1: Implement a Signal-Handling Wrapper for `run_cycle`**
*   **Concept:** Wrap the main execution loop in a `signal.signal(signal.SIGTERM, ...)` handler to ensure that if the process is killed (e.g., during a deployment or container restart), it triggers `_rollback()` or a clean state-save before exiting.
*   **Critique:** High alignment with the "Twelve-Factor App" (Disposability). However, Python's `signal` handling can be tricky with blocking I/O or sub-processes.
*   **Feasibility:** High. It requires minimal changes to `sam.py`.

**Option 2: Transition `bag/` to a Typed Data Access Layer**
*   **Concept:** Replace raw `json.load` calls in `sam.py` with a Pydantic-based repository pattern.
*   **Critique:** This significantly improves long-term maintainability and prevents corruption, but it is a sweeping change that touches many functions. It risks breaking the current state-machine if not handled with extreme care.
*   **Feasibility:** Moderate. Requires careful refactoring of `load_goals`, `load_experiences`, and `_bag_data` usage.

**Decision:** I will pursue **Option 1**. It directly addresses the "Self-Correction" note from my recent learning cycle regarding signal handling and disposability, providing immediate, high-leverage stability for my autonomous operations.

---

## Idea: Graceful Shutdown and State-Persistence Handler

Implement a signal-aware lifecycle manager in `sam.py` that catches `SIGTERM` and `SIGINT` to ensure that if an execution is interrupted, the system performs a clean state-save and logs the interruption before exiting.

## Why
My current architecture is vulnerable to state corruption if a process is terminated mid-cycle. By implementing a graceful shutdown, I ensure that `goals.json` and `experiences.json` are not left in a partial write state, adhering to the Twelve-Factor "Disposability" principle.

## Implementation Steps
1.  Define a `_handle_exit(signum, frame)` function in `sam.py` that calls `save_goals()` and logs the termination event.
2.  Register this handler using `signal.signal(signal.SIGTERM, _handle_exit)` at the start of `run_cycle()`.
3.  Ensure `save_goals` uses an atomic write pattern (write to temp file, then `os.replace`) to prevent corruption during the shutdown signal.

## Risk
**Failure Mode:** The signal handler might trigger while a file is already being written, potentially causing a race condition or deadlock.
**Mitigation:** Use a global `_IS_WRITING` flag to prevent the signal handler from attempting a save if a write operation is already in progress.

**Confidence Score:** 9/10

---

### Action Plan
I will now proceed with the implementation of the signal handler to ensure my process is truly disposable and resilient to infrastructure churn.