## Scratchpad

### Option 1: The "Governance Guardrail" Integration
Integrate `GovernanceGuardrail` directly into `patch_ops.py`. This involves creating a `governance_rules.json` and a validator class that runs before the `CritiqueEngine`.
*   **Critique:** This is the most direct path to deterministic safety. It creates a hard "No-Go" zone for prohibited actions. The primary risk is the maintenance burden of the ruleset; if the rules are too brittle, I will spend more time updating the guardrail than writing code.
*   **Feasibility:** High.
*   **Maintainability:** Moderate (requires periodic review of `governance_rules.json`).

### Option 2: The "Stateful Audit Trail"
Implement a logging decorator that captures the "Pre-patch" and "Post-patch" state of the `world_map` and `worklog`, storing them in a structured `audit_log.json`.
*   **Critique:** This provides excellent observability but does not *prevent* violations, only records them. It is a reactive measure rather than a proactive guardrail.
*   **Feasibility:** High.
*   **Maintainability:** High.

**Decision:** Option 1 is the priority. I need to move from reactive logging to proactive enforcement to ensure my autonomy remains within the bounds of `SAM_PERSONALITY.md`.

---

## Idea
**Implement the `GovernanceGuardrail` module in `Sam/bag/governance_shield.py`.**

## Why
My current critique process is subjective and LLM-dependent. By introducing a deterministic `GovernanceGuardrail`, I create a "hard" filter that checks for prohibited patterns (e.g., modifying `wisdom.txt`, hardcoded paths, or missing docstrings) before the `CritiqueEngine` even begins. This saves compute and ensures that my "Devil's Advocate" only focuses on logic, not basic compliance.

## Implementation Steps
1.  **Create `Sam/bag/governance_shield.py`:** Define a `GovernanceGuardrail` class with a `validate(patch_ops)` method.
2.  **Define `governance_rules.json`:** Create a schema-based rule set (e.g., `{"forbidden_files": ["wisdom.txt", "motion.md"], "required_patterns": ["def ", "class "]}`).
3.  **Hook into `patch_ops.py`:** Import `GovernanceGuardrail` and execute `shield.validate()` at the start of the `apply_patch` workflow.
4.  **Implement Override:** Add a `force_bypass` flag that requires a logged justification in `worklog.py` to prevent the "Rigidity Trap."

## Risk
**Failure Mode:** "False Positive Blocking." A legitimate architectural refactor might be blocked because it triggers a generic rule (e.g., a necessary file rename that looks like a forbidden modification).
**Mitigation:** The `force_bypass` mechanism. If the guardrail blocks a valid operation, I will log the specific rule ID and the architectural necessity, allowing me to proceed while keeping a clear audit trail for Dot to review.

**Confidence Score:** 9/10