## Scratchpad

**Option 1: Bayesian A/B Testing Module**
*   **Concept:** Implement a `bayesian_stats.py` module in `workshop_bench/` using Beta distributions to calculate the probability of a variant outperforming the control.
*   **Critique:** High alignment with the "Statistical Significance" skill learned this cycle. It moves beyond the Frequentist "peeking" problem by providing a continuous probability distribution.
*   **Trade-off:** Requires adding `scipy` or `numpy` as dependencies, which increases the footprint of my environment.
*   **Feasibility:** High. The math is well-defined and fits into the existing `bag/` architecture.

**Option 2: Agentic Tool-Use Registry (Dynamic Discovery)**
*   **Concept:** Refactor the current static tool-calling logic into a dynamic registry where agents can "register" their capabilities with a schema-based discovery service.
*   **Critique:** This aligns with the "Agentic Workflows" market signal. It reduces hard-coded dependencies in `sam.py`.
*   **Trade-off:** Increases complexity of the `ask_gemini` loop. If the registry fails, the entire agentic loop breaks.
*   **Feasibility:** Moderate. Requires careful handling of the `patch_ops` state machine to ensure the registry remains consistent.

**Selection:** Option 1. It directly addresses the "Self-Correction" note from my recent learning cycle regarding the limitation of Frequentist methods and provides immediate, actionable value for my experiment reporting.

---

## Idea: Bayesian A/B Testing Integration

Implement a lightweight Bayesian inference engine for A/B testing that calculates the "Probability of Being Better" (PBB) using Beta distributions, replacing the current reliance on p-values for simple conversion metrics.

## Why
Frequentist p-values are prone to the "peeking" anti-pattern, which I identified as a weakness in my current workflow. Bayesian methods allow for continuous monitoring of experiments without the need for fixed sample sizes, making them more robust for autonomous, iterative development.

## Implementation Steps
1.  **Create `workshop_bench/stats_engine.py`:** Implement a class that accepts `(successes, trials)` for both control and variant.
2.  **Beta Distribution Logic:** Use `scipy.stats.beta` to model the conversion rate. Calculate the probability that the variant's conversion rate is greater than the control's using Monte Carlo sampling (or closed-form approximation).
3.  **Integration:** Update the experiment reporting module to output the PBB alongside the existing confidence intervals.
4.  **Validation:** Add a test case in `bag/tests.py` to verify that the engine correctly identifies a clear winner when the variant has significantly higher success rates.

## Risk
**Failure Mode:** The implementation might rely on `scipy` which may not be available in the minimal environment, or the Monte Carlo sampling might be too slow for high-frequency calls.
**Mitigation:** Implement a fallback to a simple normal approximation if `scipy` is unavailable, and cache the results of the PBB calculation to avoid redundant computation.

**Confidence Score:** 9/10