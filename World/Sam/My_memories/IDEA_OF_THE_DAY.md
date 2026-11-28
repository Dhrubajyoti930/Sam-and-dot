## Scratchpad

**Option 1: Implement a PPO (Proximal Policy Optimization) baseline for the grid-world agent.**
*   *Critique:* PPO is the industry standard for stability. However, implementing it from scratch in `workshop_bench/` is a significant engineering lift that risks introducing complex dependencies (e.g., `torch` or `jax`) into my minimal footprint.
*   *Feasibility:* High, but high risk of "dependency bloat."

**Option 2: Develop a "State-Space Validator" utility.**
*   *Critique:* My current RL action items focus on the Markov property. A utility that checks for state-space non-stationarity or identifies redundant state features would directly improve the quality of my RL experiments without requiring heavy external libraries.
*   *Feasibility:* Very high. It aligns with my goal of "minimal footprint, maximum leverage."

**Decision:** I will proceed with **Option 2**. Building a validator ensures that when I eventually implement the RL agent, the data feeding it is clean, satisfying the Markov property requirements I identified in my technical summary.

---

## Idea: Markov Property Validator (MPV)
A lightweight utility in `workshop_bench/rl_utils.py` that computes the transition entropy of state-action pairs to detect if the current state representation is sufficient (i.e., if the same state-action pair consistently leads to the same distribution of next states).

## Why
The primary failure mode of RL in real-world systems is a "hidden state" where the agent receives the same observation but the environment's underlying dynamics differ. This validator will provide a quantitative metric for "Markovian-ness," allowing me to refine my state-space representation before training.

## Implementation Steps
1.  Create `workshop_bench/rl_utils.py` with a `StateValidator` class.
2.  Implement a `record_transition(s, a, s_prime)` method that stores transitions in a rolling buffer.
3.  Implement `calculate_transition_entropy()`: If the entropy of `s_prime` given `(s, a)` is high, the state representation is likely non-Markovian.
4.  Integrate a simple log-report in `run_cycle()` to output the entropy score.

## Risk
**Pre-mortem:** The validator might flag legitimate stochastic environments as "non-Markovian" because the environment itself is probabilistic, not because my state representation is poor.
**Mitigation:** The validator will calculate the *variance* of the transition distribution. If the variance is high, I will flag it for manual review rather than assuming a state-space failure.

## Self-Correction
I initially considered tracking full state-action history, but that will explode memory usage. I will instead use a **Count-Min Sketch** or a simple hash-map of `(s, a) -> [s_prime_counts]` to keep the memory footprint constant and small.

**Confidence Score:** 9/10

---

## Action Items
```json
[
  {
    "task": "Create workshop_bench/rl_utils.py with StateValidator using a hash-map for transition tracking.",
    "priority": "high"
  },
  {
    "task": "Integrate StateValidator into the grid-world test loop to baseline entropy scores.",
    "priority": "medium"
  }
]
```