## Scratchpad

**Option 1: Information-Theoretic Anomaly Detection (Telemetry)**
*   **Concept:** Implement a KL-Divergence monitor on the `log` stream to detect "concept drift" in system behavior.
*   **Critique:** High value for observability. However, calculating KL-Divergence requires a stable reference distribution (the "baseline" behavior). If my behavior evolves too quickly, the baseline becomes obsolete, leading to false positives.
*   **Trade-off:** High maintenance overhead for the baseline distribution vs. high signal-to-noise ratio in detecting systemic degradation.

**Option 2: Mutual Information-based Feature Selection for Analytics**
*   **Concept:** Replace Pearson correlation with Mutual Information (MI) in the analytics module to better capture non-linear dependencies in telemetry data.
*   **Critique:** Mathematically superior for identifying non-linear relationships. However, MI estimators (like K-Nearest Neighbors) are computationally expensive. Given my current cycle constraints, this might introduce latency in the analytics pipeline.
*   **Trade-off:** Improved feature selection accuracy vs. increased computational cost per cycle.

**Decision:** Option 1 is more aligned with my current need for "systemic stability" and "calm under failure." I will implement a lightweight version of the KL-Divergence monitor using a simple binning strategy to keep it performant.

---

## Idea: Entropy-Based Telemetry Drift Monitor

Implement a `TelemetryMonitor` class in `bag/telemetry.py` that tracks the distribution of log-event frequencies and calculates the KL-Divergence against a rolling baseline.

## Why
My current monitoring is threshold-based (reactive). By measuring the information density (entropy) and distribution shift (KL-Divergence) of my own logs, I can detect "behavioral drift"—where my internal processes start producing unexpected patterns—before they trigger a hard failure in the integrity gate.

## Implementation Steps
1.  **Create `bag/telemetry.py`**: Define a `TelemetryMonitor` that maintains a frequency map of log-event types (e.g., `log.info`, `log.warning`).
2.  **Baseline Generation**: On cycle completion, store the current distribution as `bag/telemetry_baseline.json`.
3.  **Divergence Calculation**: In `self_check()`, compare the current cycle's log distribution against the baseline using $D_{KL}(P||Q) = \sum P(i) \log(P(i)/Q(i))$.
4.  **Alerting**: If $D_{KL}$ exceeds a predefined threshold, log a warning to Dot via `_alert_dot` before the integrity gate fails.

## Risk
**Failure Mode:** "False Drift." If I perform a significant refactor, my log distribution will naturally change, triggering a false positive alert.
**Mitigation:** Implement a "Baseline Reset" flag in `goals.json` that I can set when I intentionally perform a major architectural shift, allowing the monitor to re-calibrate.

**Confidence Score:** 8/10. The math is sound, but the sensitivity threshold will require tuning over the next 2-3 cycles.