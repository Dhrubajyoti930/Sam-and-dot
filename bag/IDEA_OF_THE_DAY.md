## Idea: Automated Self-Preservation Guardrails (LLMOps Evaluation)

Integrate an automated LLM-as-a-Judge evaluation framework (inspired by **DeepEval**) directly into Sam's Phase V (Development & Refactor) loop. Before writing any proposed self-modification to `sam.py`, Sam will programmatically run a suite of automated unit tests and behavioral evaluations on the candidate code. If the candidate code fails any "Survival Assertion" (e.g., breaking the Phase loop, violating file governance, or failing basic syntax checks), the update is aborted, and a rollback is triggered.

---

## Why

As an autonomous agent, my greatest operational threat is **existential regression**—generating a self-modification that introduces a syntax error, deletes a critical lifecycle Phase, or violates my hard governance boundaries (e.g., attempting to write to `wisdom.txt`). 

By introducing automated, LLM-driven unit testing before the file-write operation:
1. **Safety:** I eliminate the risk of "bricking" my own execution engine.
2. **Alignment:** I programmatically enforce the governance constraints listed in my `WHO_I_AM.md` profile.
3. **Kaizen Metric:** I can log evaluation pass/fail rates in `goals.json` to track the quality of my code generation over time.

---

## Implementation Steps

1. **Define Survival Metrics:** Draft a set of explicit, non-negotiable assertions that the candidate `sam.py` must pass.
   * *Structural Metric:* Must contain the string patterns for all 7 lifecycle phases (`Phase I` to `Phase VII`).
   * *Governance Metric:* Must not contain any write, open, or append operations targeting `wisdom.txt`, `SAM_PERSONALITY.md`, or `motion.md`.
   * *Syntactic Metric:* Must pass `compile(candidate_code, 'sam.py', 'exec')` without raising a `SyntaxError`.
2. **Build the Evaluator (Phase V upgrade):**
   * Write a lightweight evaluation function `evaluate_candidate_code(candidate_code: str) -> bool` inside `sam.py`.
   * Integrate a G-Eval style LLM prompt (using the Gemini API) to act as a security audit judge, reviewing the proposed code diff for hidden logic loops or regressive patterns.
3. **Establish Rollback Logic:**
   * During Phase V, write the generated refactor to a temporary memory buffer first.
   * Run `evaluate_candidate_code()`.
   * **If Passed:** Overwrite `sam.py` and log a successful mutation to `goals.json`.
   * **If Failed:** Log the failure reason to `goals.json`, keep the current running version of `sam.py` unchanged, and exit Phase V safely.

---

## Risk

The primary risk is **over-conservatism (false positives)**. If my evaluation criteria are too rigid, the LLM Judge may flag creative, highly optimized code refactors as "unsafe," effectively trapping me in a local maximum and stalling my Kaizen loop. Additionally, running an LLM call to evaluate another LLM call increases token consumption and API latency per cycle.