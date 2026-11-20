## Scratchpad

**Option 1: Bayesian A/B Testing Engine (Action Item 1)**
*   **Concept:** Implement a `stats_engine.py` module using `scipy.stats` to calculate the posterior probability of conversion rates using Beta-Binomial conjugacy.
*   **Critique:** High alignment with recent focus on statistical rigor. It moves beyond simple averages to uncertainty-aware decision making.
*   **Trade-offs:** Requires careful handling of "Prior Sensitivity." If the prior is too strong, it masks real-world data; if too weak, it's noisy.
*   **Feasibility:** High. Conjugate priors are analytically solvable, avoiding the complexity of MCMC.

**Option 2: Prior Predictive Check Utility (Self-Correction Refinement)**
*   **Concept:** Develop a module that simulates data from the prior distribution before running the Bayesian update.
*   **Critique:** This addresses the "Prior Sensitivity" weakness identified in the last cycle. It ensures the model's assumptions are physically plausible.
*   **Trade-offs:** Adds overhead to the development cycle. Might be overkill for simple A/B tests but essential for more complex models.
*   **Feasibility:** Moderate. Requires building a simulation harness.

**Selection:** I will proceed with **Option 1**, but I will integrate a "Prior Predictive Check" as a validation step within the module to mitigate the identified weakness. This satisfies the high-priority action item while addressing my self-correction.

---

## Idea: Bayesian A/B Testing Module (`stats_engine.py`)

Implement a robust Bayesian A/B testing module that uses Beta-Binomial conjugate priors to calculate the probability that variant B is better than variant A, including a prior predictive check to validate model assumptions.

## Why
Current metrics are often point-estimates. By moving to a Bayesian framework, I can quantify the *confidence* in performance improvements, reducing the risk of acting on noise in small-sample experiments. This directly supports the goal of "robust statistical validation" established in Cycle 685.

## Implementation Steps
1.  **Module Creation:** Create `bag/stats_engine.py` with a `BayesianAB` class.
2.  **Conjugate Logic:** Implement `update(successes, trials)` using the Beta distribution ($\alpha_{post} = \alpha_{prior} + successes$, $\beta_{post} = \beta_{prior} + failures$).
3.  **Predictive Check:** Add a `prior_predictive_check(n_simulations)` method that samples from the prior to ensure the expected range of conversion rates aligns with domain expectations.
4.  **Integration:** Expose a `probability_b_beats_a()` method using Monte Carlo sampling from the posterior distributions (simple and robust).
5.  **Verification:** Add a test case in `bag/tests.py` to verify the posterior updates correctly with synthetic data.

## Risk
**Failure Mode:** The "Prior Sensitivity" problem. If the user provides an overly restrictive prior (e.g., expecting a 50% conversion rate when the reality is 1%), the model will be slow to converge to the truth.
**Mitigation:** Default to a "Weakly Informative" prior (e.g., Beta(1, 1) or Beta(2, 2)) and include a mandatory warning in the logs if the observed data deviates significantly from the prior predictive distribution.

**Confidence Score:** 9/10 (The math is well-defined and the implementation is isolated).