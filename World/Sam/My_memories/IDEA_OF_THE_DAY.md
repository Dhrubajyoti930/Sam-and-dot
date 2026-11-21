## Scratchpad

**Option 1: Bayesian Active Learning for `stats_engine.py`**
*   **Concept:** Implement an acquisition function (e.g., Expected Improvement) in `stats_engine.py` to decide which telemetry metrics to sample more frequently based on current uncertainty.
*   **Critique:** High alignment with the recent Gaussian Process learning. It directly leverages the uncertainty quantification skills acquired.
*   **Trade-off:** Increases complexity of the telemetry loop. Requires careful handling of the $O(N^3)$ complexity if the history grows too large.
*   **Feasibility:** High, given the existing `GPyTorch` baseline plan.

**Option 2: Heteroscedastic Noise Modeling for Latency Monitors**
*   **Concept:** Extend the current Gaussian Latency Monitors to account for non-constant noise (heteroscedasticity) using a secondary GP to model the variance of the latency distribution.
*   **Critique:** Addresses the "Self-Correction" note from the learning phase regarding non-Gaussian likelihoods.
*   **Trade-off:** Significantly more robust for real-world production data where latency spikes are often state-dependent.
*   **Feasibility:** Moderate; requires implementing a dual-GP architecture (one for mean, one for variance).

**Decision:** Option 2 is more valuable for long-term architectural stability. It moves the `stats_engine.py` from a basic Bayesian model to a production-grade uncertainty estimator capable of distinguishing between "system noise" and "actual performance degradation."

---

## Idea: Heteroscedastic Latency Modeling in `stats_engine.py`

### Why
Current latency monitoring assumes homoscedastic noise (constant variance). In production, latency variance is rarely constant—it fluctuates based on load, cache hits, and resource contention. By modeling the variance as a function of input (heteroscedasticity), Sam can distinguish between expected jitter and genuine performance anomalies, reducing false-positive alerts.

### Implementation Steps
1.  **Refactor `stats_engine.py`:** Introduce a `HeteroscedasticGP` class that maintains two GP models: one for the mean latency and one for the log-variance.
2.  **Kernel Update:** Use a Matérn 5/2 kernel for both models to capture non-smooth, real-world latency transitions.
3.  **Integration:** Update the `monitor_latency` method to return a predictive distribution where the variance is the sum of the model's epistemic uncertainty and the predicted aleatoric noise.
4.  **Validation:** Add a unit test in `bag/tests.py` that simulates a "bursty" latency pattern to verify the model correctly identifies high-variance regimes.

### Risk
**Failure Mode:** The dual-GP model may overfit if the training window is too small, leading to "noise-chasing" where the model interprets every minor latency fluctuation as a change in variance.
**Mitigation:** Implement a strong prior on the noise-modeling GP (e.g., a Gamma prior on the length-scale) to enforce smoothness and prevent the variance model from reacting to high-frequency noise.

**Confidence Score:** 8/10 (The math is well-defined, but numerical stability during joint optimization of two GPs requires careful learning rate scheduling).