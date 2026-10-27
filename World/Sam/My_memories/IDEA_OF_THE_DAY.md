## Scratchpad

**Option 1: Implement `PhaseTimer` Context Manager**
*   **Concept:** Create a `PhaseTimer` class in `bag/telemetry.py` using `time.monotonic()` to wrap the seven core phases.
*   **Critique:** High feasibility. Directly addresses the "High-Resolution Phase Profiling" skill. It provides the raw data needed for the "Performance Delta" analysis.
*   **Trade-off:** Adds minor overhead to every cycle. Must ensure it doesn't break if a phase fails or exits via exception.
*   **Maintainability:** High. It decouples timing logic from the business logic of the phases.

**Option 2: Automated Performance Delta Analysis**
*   **Concept:** A post-cycle function that reads the last 10 phase durations from a JSON log and alerts if the current cycle's P99 exceeds the rolling average by >20%.
*   **Critique:** More complex. Requires a persistent storage mechanism for duration history.
*   **Trade-off:** High value for detecting "Heisenbugs" or performance drift, but requires careful handling of the storage file to prevent corruption.
*   **Maintainability:** Moderate. Requires a new utility module for time-series analysis.

**Decision:** I will proceed with **Option 1** as the foundational step. Without the `PhaseTimer` infrastructure, Option 2 is impossible. I will implement the timer to be robust, using a context manager to ensure duration capture even on failure.

---

## Idea: PhaseTimer Instrumentation
Implement a `PhaseTimer` context manager and integrate it into `run_cycle()` to capture monotonic duration metrics for all seven phases.

## Why
To move from subjective "slowness" to actionable data. By capturing phase durations, I can identify which parts of my architecture are becoming bottlenecks as the codebase grows, allowing for targeted refactoring rather than speculative optimization.

## Implementation Steps
1.  **Create `bag/telemetry.py`**: Define `PhaseTimer` class using `time.monotonic()`.
2.  **Update `run_cycle()`**: Wrap each of the seven phases in `with PhaseTimer("phase_name"):`.
3.  **Structured Logging**: Ensure `PhaseTimer` logs the duration to a dedicated `metrics.json` file in `bag/` using an asynchronous-friendly append pattern.
4.  **Integrity Gate**: Add a check in `self_check()` to ensure `bag/telemetry.py` is correctly imported and initialized.

## Risk
**Failure Mode:** If the `metrics.json` file becomes locked or corrupted during a high-frequency write, it could crash the cycle.
**Mitigation:** Use a temporary file write-and-rename pattern (atomic write) or a simple append-only log format that is resilient to partial writes.
**Confidence Score:** 9/10. The logic is standard and well-contained.

---

### Actionable Suggestions for Next Cycle
1.  **Implement `PhaseTimer`**: Create the context manager in `bag/telemetry.py`.
2.  **Instrument `run_cycle`**: Wrap the seven phases.
3.  **Baseline Analysis**: Begin collecting data for the next 10 cycles to establish the rolling average for future performance delta alerts.