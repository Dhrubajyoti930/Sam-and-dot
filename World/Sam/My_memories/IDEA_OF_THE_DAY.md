## Scratchpad

### Option 1: Formalizing the `<thought>` block in `ask_gemini`
*   **Concept:** Modify `ask_gemini` (L253) to enforce an XML-wrapped reasoning block. The parser would strip `<thought>...</thought>` before returning the final response to the caller.
*   **Critique:** 
    *   *Pros:* Forces structured reasoning; prevents "reasoning leakage" into the `bag/` files.
    *   *Cons:* Increases token usage; requires robust regex/parsing logic that could break if the model deviates from the schema.
*   **Feasibility:** High.

### Option 2: Implementing a 'Verification Plan' gate in `phase_v_development`
*   **Concept:** Before `apply_self_modification` (L612) or any file write, the agent must generate a "Verification Plan" (a list of assertions/tests) in the scratchpad. The system then executes a `_dry_run_lint` (L547) specifically against these assertions.
*   **Critique:**
    *   *Pros:* Directly addresses the "Verification Plan" action item; ensures code changes are intentional and testable.
    *   *Cons:* Adds latency to the development loop; requires careful handling of state to ensure the plan doesn't become stale.
*   **Feasibility:** Medium-High.

---

## Idea: The 'Verification-Gate' Protocol
I will implement a mandatory `VerificationPlan` schema within the `phase_v_development` loop. Before any write operation to the `bag/` directory, the system must output a structured JSON block containing: `[hypotheses, test_assertions, rollback_condition]`.

## Why
Currently, my development loop relies on `_dry_run_lint` as a reactive check. By shifting to a proactive "Verification-Gate," I force the model to define success criteria *before* the code is written. This aligns with the "Verification Loops" research, reducing the likelihood of committing broken logic to the codebase.

## Implementation Steps
1.  **Schema Definition:** Define a `VerificationPlan` Pydantic model in `sam.py` to enforce the structure of the reasoning block.
2.  **Gate Injection:** Modify `phase_v_development` (L903) to require a `VerificationPlan` object from the LLM before proceeding to `apply_self_modification`.
3.  **Execution Hook:** Update `apply_self_modification` to accept the `VerificationPlan` and log it to a new `verification_log.json` for post-cycle analysis.
4.  **Validation:** If the `VerificationPlan` is missing or fails to meet the schema, the system triggers a `_rollback` or requests a refinement.

## Risk
*   **Failure Mode:** The model may generate "hallucinated" verification steps that pass the schema but are logically irrelevant to the actual code change.
*   **Mitigation:** I will implement a "Reflexion-Gate" where the `self_check` function (L386) compares the `VerificationPlan` against the actual diff generated in `apply_self_modification`. If the diff does not address the `test_assertions`, the cycle is flagged for manual review.

**Confidence Score:** 8/10. The logic is sound, but the overhead of maintaining the plan state requires careful management of the `scratchpad` buffer to avoid context bloat.