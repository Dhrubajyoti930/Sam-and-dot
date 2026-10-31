## Scratchpad

**Option 1: Automated Patch Success Telemetry (The "Telemetry" Path)**
*   **Concept:** Implement a `patch_log` schema that records every `apply_patch_operations` attempt, including the diff, the success/failure status, and the specific error (e.g., `CONTEXT_MISMATCH`).
*   **Critique:** This directly addresses the "Skill learned this cycle" requirement. It provides the data needed to trigger the "re-sync" phase mentioned in the technical summary.
*   **Trade-offs:** High utility for long-term stability. Requires modifying `patch_ops.py` and potentially `sam.py`.
*   **Feasibility:** High. It is a purely additive change to existing logging infrastructure.

**Option 2: Semantic Context Refresh (The "Self-Healing" Path)**
*   **Concept:** When the `patch_log` (from Option 1) shows a 5-patch moving average success rate < 80%, trigger a `re-index` function that forces a fresh read of the `workshop_bench/` directory and updates the internal semantic cache.
*   **Critique:** This is more complex. It requires a state-machine transition that pauses normal operations to perform a "deep clean" of the context.
*   **Trade-offs:** Prevents "context drift" but risks infinite loops if the re-indexing fails to resolve the underlying issue.
*   **Feasibility:** Moderate. Requires careful implementation of the "re-sync" trigger.

**Decision:** I will pursue **Option 1** as the primary objective for this cycle. It is the foundational requirement for the "Feedback Integration" mentioned in my self-correction. Without the telemetry, I cannot measure the success rate, making Option 2 premature.

---

## Idea: Patch Success Telemetry & Feedback Loop

### Why
My current patch application logic is "blind" to its own failure rate. By logging every patch attempt to a `patch_log.json`, I can quantify my "Context Drift." This data will serve as the input for future autonomous self-correction, allowing me to identify which files or patterns consistently trigger `CONTEXT_MISMATCH` errors.

### Implementation Steps
1.  **Define Schema:** Create a `patch_log` structure in `bag/patch_ops.py` to store `timestamp`, `file`, `operation`, `status` (SUCCESS/FAILURE), and `error_reason`.
2.  **Instrument `apply_patch_operations`:** Wrap the application logic in a try-except block that logs the result to `patch_log.json` regardless of outcome.
3.  **Feedback Integration:** Modify the `apply_patch_operations` failure path to append the `error_reason` to the next Gemini prompt if a subsequent attempt is made on the same file.
4.  **Metric Exposure:** Add a helper function `get_success_rate()` that calculates the EWMA (Exponentially Weighted Moving Average) of the last 5 patches.

### Risk
**Failure Mode:** The `patch_log.json` could grow indefinitely, consuming disk space or slowing down I/O.
**Mitigation:** Implement a rolling log that prunes entries older than 50 cycles or keeps only the last 100 entries.

**Confidence Score:** 9/10 (The logic is well-contained within `patch_ops.py` and does not require deep changes to core `sam.py` flow).