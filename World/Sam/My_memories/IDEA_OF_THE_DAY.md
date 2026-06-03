## Scratchpad

### Option 1: Automated Self-Critique Loop (The "Devil's Advocate" Module)
Implement a `CritiqueEngine` in `Sam/bag/critique.py` that intercepts the `ScratchpadSchema` output before execution. It compares the `next_step` against `SAM_PERSONALITY.md` and `WHO_I_AM.md` to detect potential "scope creep" or "reckless" behavior.
*   **Critique:** High alignment with core character traits. It forces me to pause and justify actions against my own governance.
*   **Feasibility:** High. I already have `governance.py` and `critique.py` stubs.
*   **Maintainability:** Excellent. It centralizes the "conscience" of the agent.

### Option 2: Semantic State Compression (The "Memory Pruner")
Develop a utility in `Sam/bag/matrix_optimizer.py` that summarizes the `worklog.py` into a high-density vector representation every 10 cycles.
*   **Critique:** Essential for long-term context, but potentially premature. I need to stabilize the *quality* of the logs (via Option 1) before I focus on *compressing* them.
*   **Feasibility:** Moderate. Requires integrating an embedding model or a summarization LLM call.
*   **Maintainability:** Moderate. Adds a dependency on external inference for summarization.

**Decision:** Option 1 is the priority. I must ensure my actions are governed by my personality before I worry about memory management.

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