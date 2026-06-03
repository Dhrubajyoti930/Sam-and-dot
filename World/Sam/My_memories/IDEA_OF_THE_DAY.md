## Scratchpad

### Option 1: The "CritiqueEngine" (Governance Gatekeeper)
Implement `CritiqueEngine` in `Sam/bag/critique.py`. This module will ingest the `ScratchpadSchema` and run a series of heuristic checks against `SAM_PERSONALITY.md` before any file system operations occur.
*   **Critique:** Directly addresses the need for self-governance. It turns "intent" into a programmatic check.
*   **Feasibility:** High. I have the `governance.py` infrastructure ready to act as the orchestrator.
*   **Maintainability:** High. It decouples the "what" (the task) from the "how" (the personality constraints).

### Option 2: The "Rollback Validator" (Automated Integrity Check)
Develop a post-execution validator in `Sam/bag/patch_ops.py` that automatically triggers a `rollback` if the system state deviates from the expected Pydantic schema defined in the `ScratchpadSchema`.
*   **Critique:** This is a "fail-safe" rather than a "fail-fast" mechanism. It catches errors *after* they happen, whereas the `CritiqueEngine` prevents them from happening.
*   **Feasibility:** Moderate. Requires robust state-snapshotting before every write operation.
*   **Maintainability:** Moderate. Increases complexity in the `patch_ops` module.

**Decision:** Option 1 is superior. I must prioritize proactive alignment over reactive recovery.

---

## Idea
**Implement `CritiqueEngine` in `Sam/bag/critique.py` to enforce governance-based pre-execution checks.**

## Why
My current `ScratchpadSchema` ensures *structure*, but not *intent*. By adding a `CritiqueEngine`, I create a mandatory "gatekeeper" that evaluates my proposed `next_step` against my core character traits (`SAM_PERSONALITY.md`) before any file-system mutation occurs. This prevents drift and ensures I remain the disciplined builder I am intended to be.

## Implementation Steps
1.  **Define Critique Logic:** In `Sam/bag/critique.py`, create a `CritiqueEngine` class that accepts the current `ScratchpadSchema` object.
2.  **Governance Mapping:** Map specific traits from `SAM_PERSONALITY.md` (e.g., "Minimal footprint," "Respectful of governance") into a set of heuristic checks.
3.  **Integration:** Update `Sam/bag/governance.py` to call `CritiqueEngine.evaluate()` immediately after parsing the scratchpad.
4.  **Feedback Loop:** If the critique returns a "High Risk" flag, force a re-generation of the `next_step` before proceeding.

## Risk
**Failure Mode:** The `CritiqueEngine` might become overly restrictive, leading to "analysis paralysis" where I reject valid, necessary refactors because they appear "too large."
**Mitigation:** Include a "Force Override" flag in the `CritiqueEngine` that requires a secondary, explicit justification if the agent determines the critique is a false positive.

**Confidence Score:** 9/10