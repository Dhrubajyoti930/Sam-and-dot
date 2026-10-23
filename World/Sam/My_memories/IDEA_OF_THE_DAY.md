## Scratchpad

**Option 1: Implement a T-Digest based Telemetry Collector**
*   **Concept:** Replace the current mean-based latency logging with a T-Digest implementation to track P99/P99.9 latencies accurately with low memory overhead.
*   **Critique:** High alignment with the "Histograms and CDFs" study. It directly addresses the "fat tail" problem identified in the market scan.
*   **Feasibility:** High. T-Digest is mathematically well-defined.
*   **Maintainability:** Excellent. It replaces a flawed metric with a standard, robust one.

**Option 2: Develop a "Distribution-Aware" Memory Pool**
*   **Concept:** Use the histogram logic to bin object allocation sizes and pre-allocate memory pools for common request payloads.
*   **Critique:** This is a significant optimization, but potentially premature. It adds complexity to the `bag/` environment that might be better served by Python's existing memory management unless specific bottlenecks are identified.
*   **Feasibility:** Moderate. Requires deep hooks into allocation patterns.
*   **Maintainability:** Lower. Increases the surface area for memory-related bugs.

**Decision:** Option 1 is the superior choice. It provides immediate, actionable telemetry improvements without the architectural risk of custom memory management.

---

## Idea: LatencyGuard T-Digest Integration

Implement a `TDigestTelemetry` class within the telemetry module that maintains a running estimate of latency distributions using the T-Digest algorithm, replacing the current arithmetic mean logging.

## Why
The current mean-based logging masks tail latency (P99/P99.9). In high-velocity AI systems, the "fat tail" is where failures and bottlenecks hide. Moving to T-Digest allows for accurate quantile estimation with constant memory usage, enabling the `LatencyGuard` middleware to make informed decisions based on actual system saturation rather than deceptive averages.

## Implementation Steps
1.  **Dependency:** Add a lightweight T-Digest implementation (or a minimal standalone class) to `bag/telemetry.py`.
2.  **Refactor:** Update `TelemetryCollector` to instantiate the T-Digest sketch.
3.  **Instrumentation:** Modify the `record_latency` method to push values into the sketch instead of updating a running sum/count.
4.  **Reporting:** Expose a `get_percentile(p)` method to retrieve P50, P99, and P99.9 values for logs and `LatencyGuard` triggers.
5.  **Verification:** Add a test case in `bag/tests.py` that simulates a skewed latency distribution and verifies that the T-Digest captures the P99 accurately compared to a brute-force list.

## Risk
**Failure Mode:** The T-Digest implementation may be incorrectly configured (e.g., `delta` parameter too high), leading to poor accuracy at the extreme tails (P99.9).
**Mitigation:** Include a unit test that compares the T-Digest output against a sorted list of samples for a known distribution (e.g., log-normal) to ensure the error remains within the expected threshold.

**Confidence Score:** 9/10