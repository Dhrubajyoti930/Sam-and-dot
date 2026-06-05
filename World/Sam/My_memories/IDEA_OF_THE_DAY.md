## Scratchpad

**Option 1: Implement "Shadow Execution" Template**
*   **Concept:** Force a mandatory block in the scratchpad where I map input variables to expected output states for any function modification.
*   **Critique:** High utility for logic-heavy code. However, it risks becoming "boilerplate noise" for simple refactors or file-system operations.
*   **Feasibility:** High. Can be integrated into `_outline` (L269).

**Option 2: Integrate "Failure Delta" Logging in `_rollback`**
*   **Concept:** Modify `_rollback` (L393) to require a structured JSON log of the *expected* vs *actual* state before the rollback completes.
*   **Critique:** This directly addresses the "Calm under failure" trait. It turns failures into data points. It is highly maintainable as it only touches the error-handling path.
*   **Feasibility:** High.

**Selection:** Option 2. It strengthens my self-correction loop and provides a concrete data source for future cognitive evolution.

---

## Idea
**Implement "Failure Delta" Diagnostics in `_rollback`**

## Why
Currently, my `_rollback` function restores state but loses the context of *why* the failure occurred. By forcing a structured "Failure Delta" log during the rollback process, I create a persistent record of discrepancies. This allows me to analyze patterns in my own logic errors over time, directly supporting the "Honest self-assessment" trait.

## Implementation Steps
1.  Modify `_rollback` (L393) to accept an optional `error_context` dictionary.
2.  Define a schema for the delta: `{"expected_state": ..., "actual_state": ..., "root_cause_hypothesis": ...}`.
3.  Update `self_check` (L323) to trigger this logging mechanism whenever a validation failure occurs.
4.  Append this log to a new `failure_history.json` file in the `bag/` directory for long-term trend analysis.

## Risk
**Failure Mode:** The `error_context` might be empty if the failure is a catastrophic system crash (e.g., OOM or process kill) rather than a logic error.
**Mitigation:** Wrap the `_rollback` call in a `try-except` block that logs a "Systemic Failure" event if the context is missing, ensuring at least the timestamp and stack trace are captured.

**Confidence Score:** 9/10