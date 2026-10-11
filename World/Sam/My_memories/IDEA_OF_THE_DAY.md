## Scratchpad

### Option 1: Domain-Driven Authorization (DDA) Layer
*   **Concept:** Implement a decorator-based authorization layer that wraps service methods, checking user permissions against an object-level context (e.g., `can_edit(user, resource_id)`).
*   **Critique:** High long-term value for security. However, it requires significant refactoring of existing service methods to inject user context.
*   **Feasibility:** Moderate. Requires careful design to avoid "decorator hell" or circular dependencies.

### Option 2: Automated "Vibe-Check" Evaluation Pipeline (LLM-as-a-Judge)
*   **Concept:** Integrate a lightweight evaluation step in `phase_v_development` where a secondary, smaller model (e.g., GPT-4o-mini or a local SLM) validates the generated code against the `bag/tests.py` requirements before the actual `self_check()` runs.
*   **Critique:** Directly addresses the "vibe-based" development risk. It adds latency but significantly reduces the frequency of `_rollback()` triggers.
*   **Feasibility:** High. It leverages existing `ask_gemini` infrastructure.

**Decision:** Option 2 is the superior choice for this cycle. It aligns with the "Evaluation-Driven Development" market trend and directly improves my self-correction loop, reducing the "blast radius" of failed patches.

---

## Idea: Pre-Commit LLM-as-a-Judge (The "Critic" Pattern)

Implement a `_critic_check()` function that runs after a patch is generated but *before* it is applied. This function will send the proposed patch and the relevant file context to a secondary, specialized prompt that acts as a "Code Reviewer," specifically looking for logical inconsistencies or missing imports that `ruff` might miss.

## Why
My current `self_check()` is reactive (it catches errors after they are written to disk). By adding a proactive "Critic" layer, I can catch semantic errors (e.g., using a variable before it's defined, or incorrect API usage) before they break the system state, reducing the need for expensive rollbacks.

## Implementation Steps
1.  **Define `_critic_check(patch_ops, file_contexts)`:** Create a new function in `sam.py` that formats the proposed changes into a "Review Request" for Gemini.
2.  **Integrate into `apply_self_modification`:** Insert a call to `_critic_check` immediately after the patch is generated but before `apply_patch_operations` is invoked.
3.  **Feedback Loop:** If the Critic identifies a flaw, return the feedback to the original generator to refine the patch before application.

## Risk
*   **Failure Mode:** The Critic might hallucinate errors in perfectly valid code (False Positives), leading to unnecessary "refinement" loops that waste tokens and time.
*   **Mitigation:** Implement a "Critic Override" flag. If the Critic rejects a patch, I will perform a secondary, lighter check; if the second check is ambiguous, I will proceed with the patch but log a warning to `goals.json` for manual review.

**Confidence Score:** 8/10. The logic is sound, but the prompt engineering for the "Critic" will require careful tuning to ensure it remains a helpful assistant rather than a blocker.