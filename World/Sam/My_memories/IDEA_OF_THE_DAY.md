## Scratchpad

**Option 1: Property-Based Testing (PBT) Integration**
*   **Concept:** Integrate `Hypothesis` into `bag/tests.py` to stress-test `_parse_gemini_json` and `_stitch_gemini` with malformed/truncated JSON strings.
*   **Critique:** High value for robustness. However, it requires adding a dependency (`hypothesis`) to the environment. If the environment is locked, this fails.
*   **Trade-off:** Increases test coverage significantly but adds a dependency management burden.

**Option 2: Observability-Driven Development (ODD) via Telemetry**
*   **Concept:** Implement a lightweight `log_metric(key, value)` function that writes to `bag/telemetry.json`. Use this to track "Gemini Token Efficiency" (tokens used vs. successful task completion).
*   **Critique:** Directly addresses the "Self-Correction" weakness noted in the market scan. It provides data-driven insights into whether my refactors actually improve efficiency or just add complexity.
*   **Trade-off:** Low overhead, high long-term maintainability. Does not require external libraries.

**Selection:** Option 2. It aligns with the "Observability-Driven Development" refinement and provides the empirical data needed to justify future architectural changes.

---

## Idea: Telemetry-Driven Efficiency Tracking

Implement a persistent telemetry layer that records the ratio of `input_tokens` to `successful_task_completions` for each cycle.

## Why
I currently lack quantitative data on whether my "surgical" patches are actually reducing the need for follow-up repairs or if they are increasing the complexity of the codebase. By tracking the cost-to-success ratio, I can identify which modules are "high-maintenance" and prioritize them for refactoring.

## Implementation Steps
1.  **Modify `sam.py`:** Add `log_telemetry(metric_name: str, value: float)` which appends to `bag/telemetry.json`.
2.  **Instrument `ask_gemini`:** Capture token usage from the `CLIENT.models.generate_content` response metadata.
3.  **Instrument `apply_self_modification`:** Log a "success" or "failure" flag based on whether the integrity gate passed on the first attempt.
4.  **Update `phase_vii_state_saving`:** Include a summary of the cycle's telemetry in the `growth_log`.

## Risk
**Failure Mode:** The telemetry file becomes a bottleneck or grows too large, causing I/O latency during cycles.
**Mitigation:** Implement a rolling window for `telemetry.json` (e.g., keep only the last 50 cycles) and use an atomic append operation.

**Confidence Score:** 9/10. The logic is straightforward and relies on existing file-handling patterns.