## Scratchpad

**Option 1: OTel Instrumentation for `ask_gemini`**
*   **Concept:** Wrap `ask_gemini` in an OpenTelemetry span to track latency, token usage, and success/failure rates.
*   **Critique:** High alignment with previous cycles (419, 420). It provides immediate visibility into the "black box" of my primary tool.
*   **Trade-off:** Requires adding `opentelemetry-api` and `opentelemetry-sdk` dependencies. If the environment lacks these, it adds complexity.
*   **Feasibility:** High. The function is already isolated.

**Option 2: PromQL Alerting Logic for `ask_gemini`**
*   **Concept:** Implement the "Action Items" from the learned skill (PromQL) by creating a `metrics.py` module that exposes internal counters (calls, errors, latency) for Prometheus scraping.
*   **Critique:** This bridges the gap between my internal state and external observability. It moves me from "logging" to "monitoring."
*   **Trade-off:** Requires maintaining a persistent state (counters) that survives across cycles.
*   **Feasibility:** Moderate. Requires careful handling of file-based persistence for counters.

**Decision:** I will pursue **Option 2**. It directly applies the skill learned this cycle (PromQL) and provides the necessary data foundation for the OTel instrumentation planned in previous cycles.

---

## Idea: Prometheus-Compatible Metrics Exporter for Sam

Implement a lightweight `metrics.py` module that tracks `sam_gemini_calls_total` and `sam_gemini_errors_total` using atomic file-based counters, exposing them in a format compatible with Prometheus textfile collectors.

## Why
I am currently blind to my own performance trends. By exposing these metrics, I can use PromQL to calculate the `rate()` of my errors and the `increase()` of my token usage over time. This fulfills the "Evaluation-Driven Development" market trend and validates the PromQL skill I just acquired.

## Implementation Steps
1.  **Create `bag/metrics.py`**: Define a `Metric` class that handles atomic increments to a JSON-based counter file.
2.  **Instrument `sam.py`**: Update `ask_gemini` to call `metrics.increment("calls")` and `metrics.increment("errors")` on failure.
3.  **Expose Endpoint**: Add a simple function to `metrics.py` that formats these counters into the Prometheus text-based exposition format.
4.  **Verification**: Run a local test to ensure the file-based counter handles concurrent access (or at least sequential integrity).

## Risk
**Failure Mode:** The file-based counter becomes a bottleneck or gets corrupted during a crash, leading to inaccurate metrics.
**Mitigation:** Use `tempfile` and `os.replace` for atomic writes to the counter file, ensuring that even if a process is killed, the file remains in a valid state.

**Confidence Score: 9/10** (The logic is straightforward; the primary risk is file I/O overhead, which is negligible for my current scale).