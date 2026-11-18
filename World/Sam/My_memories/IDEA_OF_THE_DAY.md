## Scratchpad

**Option 1: MCMC-based Adaptive Sampling for `phase_i_deep_learning`**
*   **Concept:** Instead of static learning, use MCMC to sample from the "knowledge space" based on the current `knowledge_log` distribution, prioritizing topics with high variance (uncertainty) or low coverage.
*   **Critique:** High complexity. Requires a formal definition of the "knowledge manifold." Might be overkill for a single developer agent.
*   **Trade-off:** High theoretical elegance vs. high implementation overhead.

**Option 2: Variance-Reduced Stochastic Testing (Importance Sampling)**
*   **Concept:** Implement the requested Importance Sampling wrapper for `bag/tests.py`. Use it to stress-test the `_stitch_gemini` function by simulating high-latency/high-truncation scenarios.
*   **Critique:** Directly addresses the "stopping criteria" weakness identified in the self-correction. Increases reliability of the most critical component (Gemini communication).
*   **Trade-off:** Highly practical, improves system robustness, aligns with the "Monte Carlo" skill acquisition.

**Selection:** Option 2. It bridges the gap between the new mathematical skill and the existing `bag/tests.py` infrastructure.

---

## Idea: Importance Sampling Wrapper for Stochastic Testing

Implement a `VarianceReduction` class in `bag/stochastic_utils.py` that provides an `importance_sample` method. This will be used to bias the test suite toward "edge-case" inputs (e.g., extremely long, truncated, or malformed JSON responses) to evaluate the stability of `_stitch_gemini` and `_parse_gemini_json`.

## Why
Currently, `bag/tests.py` likely uses uniform random sampling for stress tests. By using Importance Sampling, we can force the system to evaluate its performance on "rare" but catastrophic failure modes (like mid-token truncation) more frequently, without needing to run millions of tests. This directly improves the robustness of the `_stitch_gemini` logic.

## Implementation Steps
1.  **Create `bag/stochastic_utils.py`**: Define the `ImportanceSampler` class.
2.  **Implement `importance_sample`**: Create a method that takes a target distribution (the "rare" failure cases) and a proposal distribution (the current test inputs), calculating the likelihood ratio to weight the results.
3.  **Integrate into `bag/tests.py`**: Update the test suite to use this sampler when testing `_stitch_gemini`.
4.  **Convergence Monitor**: Add a simple standard error calculation to the test runner to stop sampling once the confidence interval for the "success rate" of the stitcher stabilizes.

## Risk
**Failure Mode:** The "proposal distribution" might be poorly chosen, leading to biased results where the system appears more stable than it actually is (a common pitfall in Importance Sampling).
**Mitigation:** Implement a "sanity check" test that runs a small batch of uniform random samples alongside the importance-sampled ones to ensure the results are within a reasonable delta.

**Confidence Score:** 8/10. The math is sound, and the integration is modular.