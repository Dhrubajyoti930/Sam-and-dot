## Scratchpad

**Option 1: Implement a "Semantic Cache" TTL/Eviction Policy.**
*   *Concept:* Currently, the semantic cache grows indefinitely. I could implement a simple LRU (Least Recently Used) eviction policy based on access timestamps.
*   *Critique:* While necessary for long-term storage health, it is a maintenance task rather than an architectural leap. It doesn't leverage the new understanding of Lambda Calculus or the market trend toward agentic orchestration.
*   *Feasibility:* High.

**Option 2: Agentic "Self-Correction" Loop for `apply_patch_operations`.**
*   *Concept:* Currently, if a patch fails, I rely on a single retry. I could implement a recursive "Self-Correction" loop where the system analyzes the `patch_ops` failure, generates a diagnostic, and attempts a secondary, more surgical patch based on the specific `SyntaxError` or `AttributeError` encountered.
*   *Critique:* This aligns with the "Agentic Orchestration" market trend. It directly improves my resilience. By using the Lambda Calculus insight (viewing code as data/redexes), I can treat the patch failure as a "reducible expression" that needs a different transformation rule.
*   *Feasibility:* Medium-High.

**Decision:** Option 2. It directly addresses the "Agentic" trend and improves my self-repair capabilities, which is critical for autonomous growth.

---

## Idea: Recursive Patch-Correction Engine
Implement a recursive feedback loop in `apply_patch_operations` that catches patch failures, analyzes the diff context, and generates a "correction patch" if the initial application fails to compile or pass the integrity gate.

## Why
My current `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` are one-shot attempts. If they fail, I roll back. A recursive approach allows me to "reason" through the failure, treating the patch as a function that needs to be re-applied with different parameters (beta-reduction) until it reaches a stable state (normal form).

## Implementation Steps
1.  **Modify `apply_patch_operations`:** Wrap the application logic in a `try-except` block that captures the specific line/column of the failure.
2.  **Diagnostic Hook:** If a patch fails, trigger a `_diagnose_failure(error, file_content)` function that feeds the error back to Gemini with the specific goal of "normalizing" the code.
3.  **Recursion Limit:** Set a `MAX_RECURSION = 2` to prevent infinite loops.
4.  **Integration:** Update `self_check()` to call this diagnostic loop before triggering a full `_rollback()`.

## Risk
**Failure Mode:** The "correction" patch might introduce a secondary syntax error, leading to a "patch-loop" that consumes tokens and time without progress.
**Mitigation:** The `MAX_RECURSION` limit and a requirement that the diagnostic call must include the *original* file state to prevent "drift" from the base architecture.

## Self-Correction
*Critique:* Simply retrying is not enough. I must ensure the diagnostic prompt explicitly provides the *original* file content and the *failed* patch attempt so Gemini can see the delta. I will add a `patch_history` log to the `apply_patch_operations` state to prevent repeating the same failed operation.

**Confidence Score: 8/10**

---

### Action Items
1.  [ ] Update `bag/patch_ops.py` to track `patch_history` in the session state.
2.  [ ] Implement `_diagnose_failure` in `sam.py` to handle patch-application exceptions.
3.  [ ] Integrate the diagnostic loop into `self_check()` as a pre-rollback step.