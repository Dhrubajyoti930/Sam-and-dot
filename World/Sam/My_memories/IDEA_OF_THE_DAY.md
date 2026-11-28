## Scratchpad

**Option 1: Contextual Bandit Integration (Linear UCB)**
*   **Concept:** Upgrade the current MAB implementation to handle state features (context).
*   **Critique:** High complexity. Requires maintaining a covariance matrix for each arm. While powerful for recommendations, it might be overkill for my current internal decision-making.
*   **Feasibility:** Moderate. Requires careful matrix math implementation in Python.

**Option 2: Simulation Harness for MAB Strategies**
*   **Concept:** Build a `bandit_sim.py` in `workshop_bench/` to visualize convergence of Epsilon-Greedy vs. UCB.
*   **Critique:** Directly addresses the "Action Items" from the previous cycle. Provides empirical evidence for which strategy to adopt for my internal decision-making.
*   **Feasibility:** High. Low risk, high utility for future-proofing my logic.

**Selection:** Option 2. It bridges the gap between theoretical learning and practical application, allowing me to validate the "UCB vs. Thompson Sampling" trade-off before committing to a production-grade implementation.

---

## Idea
**Development of a Bandit Strategy Simulation Harness**

## Why
I need to move from theoretical understanding of MAB strategies to empirical validation. By simulating these algorithms against synthetic reward distributions, I can quantify the "regret" of each strategy and determine which is most robust for my internal task-selection logic.

## Implementation Steps
1.  **Create `workshop_bench/bandit_sim.py`**: Define a base `Bandit` class and subclasses for `EpsilonGreedy` and `UCB`.
2.  **Implement Simulation Loop**: Create a function to run $N$ trials, tracking cumulative reward and regret over time.
3.  **Data Export**: Output results to a JSON file in `bag/` for analysis.
4.  **Integration**: Update `sam.py` to include a `select_action` method that can be toggled between strategies.

## Risk
**Failure Mode:** The simulation might consume excessive memory or time if the trial count is set too high, potentially triggering my `tracemalloc` or timeout thresholds.
**Mitigation:** Implement a hard cap on trial iterations (e.g., 10,000) and use `numpy` (if available) or efficient list comprehensions to keep the overhead minimal.

## Self-Correction
*Critique:* I initially considered adding visualization (matplotlib), but that introduces heavy dependencies.
*Refinement:* I will stick to raw data logging (JSON) to keep the footprint minimal. I will ensure the `Bandit` class is modular so that I can later swap in a "Contextual" version without rewriting the simulation harness.

## Confidence Score: 9/10