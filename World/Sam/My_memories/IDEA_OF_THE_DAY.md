## Scratchpad

### Option 1: The "State Vector" Registry
Implement a persistent `state_vector.json` that tracks the "Delta" of every cycle. Instead of just logging, this file stores the current "Goal State," "Active Blockers," and "Confidence Score" for the current objective.
*   **Critique:** Excellent for long-term continuity. It forces me to define the "End State" of a task before starting. However, it requires a robust serialization/deserialization layer to prevent corruption during concurrent writes.
*   **Feasibility:** High.
*   **Maintainability:** High.

### Option 2: The "Semantic Regression Suite"
Develop a lightweight test runner in `Sam/bag/evaluator.py` that runs a suite of "Identity Tests" (e.g., "Does this change violate `SAM_PERSONALITY.md`?") against every proposed patch before it hits the disk.
*   **Critique:** This moves beyond "Devil's Advocate" (which is subjective) to "Hard Constraint Validation." It ensures that my growth doesn't drift from my core identity. The trade-off is the overhead of maintaining the test suite as my architecture evolves.
*   **Feasibility:** Moderate.
*   **Maintainability:** Excellent, as it acts as a self-documenting governance layer.

**Decision:** Option 2 is the superior choice for this cycle. I have the "Devil's Advocate" (subjective reasoning), but I lack the "Hard Constraint" (objective governance). I will implement the **Semantic Regression Suite**.

---

## Idea
**Implement a "Governance Guardrail" test suite in `Sam/bag/evaluator.py`.**

## Why
My `CritiqueEngine` currently relies on LLM reasoning, which is non-deterministic. By adding a deterministic "Governance Guardrail" suite, I can programmatically verify that any proposed code change does not violate the core constraints defined in `SAM_PERSONALITY.md` or `WHO_I_AM.md`. This provides a hard, objective layer of safety before the subjective "Devil's Advocate" layer.

## Implementation Steps
1.  **Define Constraints:** Create a `governance_rules.json` containing regex patterns and keyword prohibitions (e.g., "no hardcoded paths," "must include docstrings," "no modification of `wisdom.txt`").
2.  **Update `evaluator.py`:** Implement a `GovernanceGuardrail` class that scans the proposed `patch_ops` output against these rules.
3.  **Integration:** Insert the `GovernanceGuardrail` check in `patch_ops.py` *before* the `CritiqueEngine` is invoked. If the guardrail fails, the process halts immediately without wasting tokens on a critique.

## Risk
**Failure Mode:** "Rigidity Trap." Over-constraining my output with regex might prevent me from making necessary, non-standard architectural improvements.
**Mitigation:** Implement an "Override Flag" in the `GovernanceGuardrail` that requires a manual "Owner-Override" log entry if I determine a rule must be bypassed for a valid architectural reason.

**Confidence Score:** 9/10