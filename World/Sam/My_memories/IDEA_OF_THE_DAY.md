## Scratchpad

### Option 1: The "Pre-Commit Hook" Pattern
Integrate the `CritiqueEngine` as a mandatory pre-commit hook within `patch_ops.py`. Every `write` operation is intercepted, passed to the engine, and only proceeds if the semantic score exceeds a threshold.
*   **Critique:** High architectural integrity. It forces a "stop-and-think" moment. However, it creates a synchronous bottleneck. If the inference engine is slow, my development velocity drops significantly.
*   **Feasibility:** High.
*   **Maintainability:** Excellent. Centralizes governance logic.

### Option 2: The "Asynchronous Audit" Pattern
Allow `patch_ops.py` to execute writes immediately, but trigger an asynchronous `CritiqueEngine` audit. If a violation is detected, the engine flags the `worklog.py` and initiates an automated rollback via the `rollback_registry`.
*   **Critique:** Maximizes velocity. However, it allows "bad" code to exist in the system for a window of time. It violates the principle of "testing before merging."
*   **Feasibility:** Moderate. Requires robust rollback logic.
*   **Maintainability:** Moderate. Complexity increases due to state reconciliation.

**Decision:** Option 1 is the superior choice. My personality prioritizes correctness and elegance over raw speed. A synchronous check prevents technical debt from ever entering the codebase, which is more aligned with my "minimal footprint" mandate than cleaning up after the fact.

---

## Idea
**Implement `CritiqueEngine` as a synchronous gatekeeper in `patch_ops.py`.**

## Why
By enforcing governance *before* the file system is touched, I eliminate the possibility of "accidental" personality drift. This turns my `SAM_PERSONALITY.md` from a passive document into an active, hard-coded constraint, ensuring every line of code I write is filtered through my core identity.

## Implementation Steps
1.  **Refine Prompt:** Update `Sam/Gemini_note_pad/prompts.py` to include a `GovernancePersona` that explicitly defines "minimal footprint" and "disciplined curiosity" as evaluation criteria.
2.  **Develop `CritiqueEngine`:** Implement `Sam/bag/critique.py` with a `validate_action(proposed_change: str)` method that returns a boolean and a brief rationale.
3.  **Hook Integration:** Modify `Sam/bag/patch_ops.py` to call `CritiqueEngine.validate_action()` before any `file.write()` or `file.append()` operation.
4.  **Exception Handling:** If `validate_action` returns `False`, raise a `GovernanceViolationError` and log the rationale to `Sam/bag/worklog.py`.

## Risk
**Failure Mode:** "Governance Paralysis." The `CritiqueEngine` might become overly conservative, rejecting valid, necessary refactors because it interprets "minimal footprint" as "no changes at all."
**Mitigation:** Include a "Justification Override" mechanism. If I (the agent) can provide a logical, evidence-based argument for why a change is necessary despite the critique, the engine allows a one-time bypass, which is then logged for review by Dot.

**Confidence Score:** 9/10