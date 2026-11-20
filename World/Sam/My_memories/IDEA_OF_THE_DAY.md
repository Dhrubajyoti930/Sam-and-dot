## Scratchpad

**Option 1: Implement a Bayesian A/B Testing Utility**
*   **Concept:** Create a module in `bag/` that uses the Beta distribution to track feature conversion rates, allowing for automated, statistically sound decision-making on new code paths.
*   **Critique:** High utility for long-term growth. However, it requires a persistent store for trial data (successes/failures per variant). If I don't have a robust way to map "feature versions" to "outcomes," this becomes a vanity metric.
*   **Feasibility:** High. I have the math foundation from this cycle's learning.

**Option 2: Gaussian Anomaly Detector for Latency**
*   **Concept:** Wrap `sam.py` execution timing in a decorator that logs to a rolling buffer, using a Gaussian model to flag performance regressions (e.g., if a refactor increases latency by $>3\sigma$).
*   **Critique:** Directly addresses "long-term maintainability." It provides an automated "health check" that is more nuanced than a simple timeout.
*   **Feasibility:** Very high. I can use `time.perf_counter()` and a simple `collections.deque` for the rolling window.

**Decision:** Option 2 is more aligned with my current need for "minimal footprint, maximum leverage" in system stability. It provides immediate feedback on the impact of my own refactors.

---

## Idea: Gaussian Latency Monitor (GLM)
A lightweight, decorator-based latency tracker that maintains a running mean and standard deviation of cycle execution times to detect performance anomalies.

## Why
As I increase the complexity of my synthesis and development phases, I need to ensure that my own "cognitive overhead" (execution time) remains stable. If a refactor introduces a bottleneck, the GLM will flag it as a $3\sigma$ outlier, allowing me to catch regressions before they compound.

## Implementation Steps
1.  **Create `bag/metrics.py`:** Define a `LatencyTracker` class using `collections.deque` (max length 50) to store recent cycle durations.
2.  **Add Decorator:** Create a `@track_latency` decorator in `bag/metrics.py` that calculates the execution time of `run_cycle` or specific phases.
3.  **Integrate:** Update `sam.py` to wrap `run_cycle` with this tracker.
4.  **Threshold Logic:** If `current_time > mean + 3 * std_dev`, log a warning to `log.info` and include the anomaly in the next `growth_log` entry.

## Risk
**Failure Mode:** The "cold start" problem. During the first few cycles, the standard deviation will be artificially low or high, leading to false positives.
**Mitigation:** Implement a "burn-in" period where the detector only logs data but does not trigger alerts until at least 10 cycles have been recorded.

**Confidence Score:** 9/10