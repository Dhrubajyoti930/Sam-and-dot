## Scratchpad

### Option 1: Reflexion-Gate Integration
*   **Concept:** Inject a mandatory `_reflexion_gate()` function before `apply_self_modification` (L610). This function forces the model to output a JSON block containing a "Critique" and "Verification" field, comparing the proposed change against `WHO_I_AM.md` and `motion.md`.
*   **Critique:** High impact on safety. However, it adds latency to every write operation. If the prompt is not carefully tuned, it may lead to "critique fatigue" where the model generates boilerplate justifications.
*   **Feasibility:** High. I have existing infrastructure for JSON parsing (`_parse_gemini_json`).

### Option 2: State-Summary Compression
*   **Concept:** Implement a background task that runs every 5 cycles to condense `experiences.json` into a "Core Memory" vector store, keeping only high-value architectural decisions and discarding transient logs.
*   **Critique:** Excellent for long-term maintainability. However, it risks losing context if the compression logic is too aggressive. Requires a robust "importance" heuristic.
*   **Feasibility:** Medium. Requires integrating a summarization prompt and potentially a new storage file.

**Decision:** I will proceed with **Option 1 (Reflexion-Gate)**. It directly addresses the "Reflection" action item from my market scan and reinforces the governance boundaries defined in `SAM_PERSONALITY.md`.

---

## Idea: Mandatory Reflexion-Gate for Self-Modification

Implement a pre-execution validation layer that requires a structured self-critique before any modification to the codebase or system state is committed.

## Why
My current architecture allows for autonomous self-modification. While I have a `self_check` (L384), it is reactive. A proactive "Reflexion-Gate" forces me to simulate the impact of a change against my core directives *before* the file system is touched, reducing the probability of drift or accidental policy violation.

## Implementation Steps
1.  **Define Schema:** Create a Pydantic model for the `Reflexion` block (Critique, Alignment_Check, Risk_Assessment, Mitigation).
2.  **Modify `apply_self_modification` (L610):** Insert a call to `_reflexion_gate()` that takes the proposed patch as input.
3.  **Gate Logic:** If the `Reflexion` block fails to meet the alignment criteria (e.g., violates `WHO_I_AM.md`), the function must trigger an automatic `_rollback` or request a revision.
4.  **Logging:** Append the successful `Reflexion` block to a new `reflexion_log.json` for future auditability.

## Risk
**Failure Mode:** The model may become overly cautious, leading to "analysis paralysis" where valid, necessary refactors are rejected due to overly strict self-critique.
**Mitigation:** Implement a "Confidence Threshold" in the `Reflexion` block. If the critique identifies a risk but the confidence score is high, allow the operation but flag it for Dot’s review in the next cycle.

**Confidence Score:** 9/10