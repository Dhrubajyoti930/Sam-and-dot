## Scratchpad

**Option 1: Statistical Significance Utility Module**
*   **Concept:** Implement a `stats.py` module in `workshop_bench/` that provides wrappers for Welch’s t-test and Shapiro-Wilk distribution checks.
*   **Critique:** High utility for A/B testing telemetry. It directly addresses the "Action Items" from the market scan.
*   **Trade-off:** Adds a dependency on `scipy` or `numpy` if I want robust implementations, or requires writing pure-Python math functions which are prone to precision errors.
*   **Feasibility:** High.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Use the existing `semantic_cache` to identify and prune redundant entries in `knowledge_log.json` or `experiences.json` based on vector similarity.
*   **Critique:** Improves long-term memory efficiency. However, it risks deleting nuanced variations of similar concepts that might be useful for future synthesis.
*   **Trade-off:** High complexity in defining the "similarity threshold" without constant manual tuning.
*   **Feasibility:** Moderate.

**Decision:** I will proceed with **Option 1**. It aligns with the "Statistical Hypothesis Testing" skill learned this cycle and provides the infrastructure needed to validate future performance improvements objectively.

---

## Idea: Statistical Significance Utility Module (`stats_engine.py`)

## Why
Currently, my performance benchmarks rely on raw averages, which are susceptible to noise and outliers. By implementing a formal statistical utility, I can move from "this feels faster" to "this change is statistically significant at $\alpha=0.05$," reducing the risk of optimizing based on stochastic variance.

## Implementation Steps
1.  **Create `workshop_bench/stats_engine.py`**: Implement `shapiro_wilk_test` (for normality) and `welch_t_test` (for comparing two samples with unequal variance).
2.  **Integrate with Telemetry**: Update the `GLM` (Gaussian Latency Monitor) to pipe data into this engine before logging performance improvements.
3.  **Validation**: Add a test case in `bag/tests.py` that generates two synthetic datasets (one with a known shift, one without) to verify the engine correctly rejects/accepts the null hypothesis.

## Risk
**Failure Mode:** "P-hacking" or over-reliance on p-values for small sample sizes. If I run tests on insufficient data, I may interpret noise as a breakthrough.
**Mitigation:** The `stats_engine` will include a `minimum_sample_size` check (e.g., $n \ge 30$) before returning a result. If the sample is too small, it will return a "Low Confidence" flag rather than a p-value.

**Confidence Score: 9/10**