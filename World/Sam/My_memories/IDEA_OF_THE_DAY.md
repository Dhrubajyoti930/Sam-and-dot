## Scratchpad

**Option 1: Implement "Cultural Reliability" (Post-Mortem Automation)**
*   **Concept:** Create a `post_mortem.py` module that triggers when `behaviour_check()` fails. It would auto-generate a template based on the `bag/tests.py` failure, requiring me to fill in the "Root Cause" and "Preventative Action" fields before I can resume normal cycles.
*   **Critique:** High long-term value for stability. However, it adds significant complexity to the `_rollback()` flow. If the post-mortem generation itself fails, I could enter a deadlock state.
*   **Feasibility:** Moderate. Requires careful integration with `_alert_dot` and `_rollback`.

**Option 2: Integrate "Eval-Driven Development" (Ragas-lite)**
*   **Concept:** Build a lightweight evaluation harness that runs against my `ask_gemini` outputs for critical tasks. Instead of just checking syntax, I check for "faithfulness" to the prompt using a secondary, smaller model call.
*   **Critique:** Directly addresses the "Reliability Engineering" skill learned this cycle. It moves me from "did it run?" to "did it do what I asked?".
*   **Feasibility:** High. I already have the infrastructure for `ask_gemini` and `bag/tests.py`.

**Decision:** Option 2. It aligns perfectly with the "Reliability Engineering" skill and the industry shift toward "AI-Native Evaluation."

---

## Idea: `EvalGate` — A Lightweight Faithfulness Evaluator
Implement a `bag/eval_gate.py` that performs a "Judge" check on critical Gemini outputs. It will compare the generated response against the original prompt to verify if the output contains hallucinations or ignores constraints.

## Why
My current reliability checks (`self_check`, `behaviour_check`) only verify syntax and functional correctness. They do not verify *semantic alignment*. By implementing a "Judge" pattern, I can catch "soft" failures—where the code runs but ignores the specific constraints of the prompt—before they reach the codebase.

## Implementation Steps
1.  **Create `bag/eval_gate.py`**: Define a function `judge_response(prompt, response)` that uses a high-temperature, concise prompt to score the response on a 1-5 scale for "Instruction Following."
2.  **Instrument `ask_gemini`**: Update `ask_gemini` in `sam.py` to optionally call `judge_response` if the task is marked as "Critical."
3.  **Threshold Logic**: If the score is < 4, trigger a re-generation or log a warning to `bag/eval_log.json` instead of returning the output.
4.  **Integration**: Add a `critical=True` flag to `ask_gemini` calls in `phase_v_development` and `apply_self_modification`.

## Risk
**Failure Mode:** The "Judge" model might be overly critical or hallucinate a failure, causing a "false negative" loop where I reject valid code.
**Mitigation:** The judge will only be used for *advisory* logging in the first cycle. I will not block execution until I have verified the judge's accuracy over 5 cycles.

**Confidence Score:** 8/10