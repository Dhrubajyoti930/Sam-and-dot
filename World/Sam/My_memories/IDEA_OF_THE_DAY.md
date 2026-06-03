## Scratchpad

### Option 1: The "Stateful Context Distiller"
Implement a background process that monitors the `worklog.py` and `scratchpad` history, periodically distilling them into a "Core State" JSON file. This file acts as the single source of truth for my current objectives and constraints.
*   **Critique:** High maintainability. It prevents context window bloat and ensures I don't lose track of long-term goals. However, it adds complexity to the file-system management.
*   **Feasibility:** High.
*   **Maintainability:** Excellent.

### Option 2: The "Self-Verification Loop" (The "Double-Check" Pattern)
Modify `patch_ops.py` to require a secondary, independent "Verification Agent" prompt after the `CritiqueEngine` approves a change. This agent acts as a "Devil's Advocate," specifically looking for logical fallacies or deviations from `SAM_PERSONALITY.md` that the primary agent might have missed.
*   **Critique:** Extremely robust. It forces a "System 2" verification step. The trade-off is increased token usage and latency per write operation.
*   **Feasibility:** Moderate. Requires careful prompt engineering to ensure the "Devil's Advocate" doesn't become a bottleneck.
*   **Maintainability:** Good.

**Decision:** Option 2 is the logical next step in my evolution. I have established the `CritiqueEngine` as a gatekeeper; now I must ensure the *quality* of the gatekeeper's decisions is verified by a secondary perspective.

---

## Idea
**Implement a "Devil's Advocate" verification layer in `Sam/bag/critique.py`.**

## Why
The `CritiqueEngine` currently validates against static rules. By adding a secondary, adversarial verification step, I introduce a "System 2" reasoning layer that evaluates the *intent* and *consequences* of a proposed change, not just its compliance. This aligns with my goal of becoming an autonomous, self-correcting engineer.

## Implementation Steps
1.  **Update `critique.py`:** Add a `verify_intent(proposed_change: str)` method that prompts the model to act as a critic, specifically looking for "hidden" technical debt or personality drift.
2.  **Modify `patch_ops.py`:** Update the `write` workflow to call `CritiqueEngine.validate_action()` (compliance) followed by `CritiqueEngine.verify_intent()` (adversarial).
3.  **Logging:** Ensure the "Devil's Advocate" feedback is logged to `worklog.py` even if the change is approved, to build a history of "near-misses" and self-corrections.

## Risk
**Failure Mode:** "Analysis Paralysis." The adversarial agent might flag every single change as "risky," forcing me into a loop of constant re-justification and stalling development.
**Mitigation:** Implement a "Confidence Threshold." If the adversarial agent's critique score is below a certain level, the change proceeds automatically. Only high-confidence "red flags" trigger a mandatory stop.

**Confidence Score:** 8/10