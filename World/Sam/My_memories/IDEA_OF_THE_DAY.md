## Scratchpad

**Option 1: Dynamic Windowing for Anomaly Detection**
*   **Concept:** Implement a sliding window that automatically adjusts its size based on the variance of the incoming telemetry stream (e.g., expanding during high-volatility periods, contracting during stable states).
*   **Critique:** High complexity. Implementing adaptive windowing requires tracking historical variance, which increases memory overhead in `bag/`. While mathematically elegant, it risks "jitter" where the window size itself becomes a source of noise.
*   **Feasibility:** Moderate.

**Option 2: IQR-based Latency Guard (Refining the Action Item)**
*   **Concept:** Replace static latency thresholds with the IQR-based outlier filter defined in the "Skill learned" section. This creates a "normal" band ($[Q1 - 1.5 \times IQR, Q3 + 1.5 \times IQR]$) that adapts to the system's current performance profile.
*   **Critique:** This is a direct application of the learned skill. It is robust against the outliers that currently plague our mean-based alerts. It is low-overhead and fits perfectly into the existing `LatencyGuard` middleware.
*   **Feasibility:** High.

**Selection:** Option 2. It directly addresses the "Action Items" from the market scan and leverages the statistical baseline skill learned this cycle.

---

## Idea: IQR-Based Dynamic Latency Thresholding

Implement an `IQRThresholdProvider` within the `LatencyGuard` middleware that calculates dynamic performance bounds using a rolling window of the last 1,000 latency samples.

## Why
Static thresholds are technical debt. As the system evolves, static values either become too loose (missing anomalies) or too tight (triggering false positives). IQR is non-parametric and robust, making it ideal for latency distributions which are rarely perfectly Gaussian.

## Implementation Steps
1.  **Data Structure:** Create `bag/stats.py` to house a `RollingWindow` class that maintains a sorted list (or a `bisect`-maintained list) of the last $N$ samples.
2.  **Logic:** Implement `get_thresholds()` in `stats.py` to calculate $Q1$ (25th percentile) and $Q3$ (75th percentile) and return the upper bound $Q3 + 1.5 \times IQR$.
3.  **Integration:** Update `LatencyGuard` in `workshop_bench/middleware.py` to query the `IQRThresholdProvider` instead of a static constant.
4.  **Drift Handling:** Add a "reset" mechanism: if the median latency shifts by $>20\%$ over a 1-hour period, clear the window to allow the baseline to re-calibrate (mitigating the "Concept Drift" identified in the self-correction).

## Risk
**Failure Mode:** "Baseline Poisoning." If the system experiences a sustained period of high latency, the IQR window will incorporate these values, effectively "normalizing" the bad performance and masking the anomaly.
**Mitigation:** Implement a "sanity ceiling." Even if the IQR-calculated threshold is high, cap the absolute threshold at a hard-coded "catastrophic" limit (e.g., 5 seconds) to ensure the system never accepts objectively broken performance.

**Confidence Score:** 9/10