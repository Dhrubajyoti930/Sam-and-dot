## Scratchpad

**Option 1: Dynamic Knowledge Graph (KG) Integration**
*   **Concept:** Replace the current `knowledge_log.json` with a local graph database (e.g., `sqlite` with `sqlite-vss` or a simple adjacency list) to map skill dependencies.
*   **Critique:** High architectural value for long-term learning. However, it introduces a new dependency and complexity in managing graph state. It might be overkill for the current scale of Sam's memory.
*   **Feasibility:** Moderate. Requires building a schema and migration logic.

**Option 2: Automated Evaluation-Driven Development (LLM-as-a-Judge)**
*   **Concept:** Implement a `phase_viii_evaluation` that uses a stronger model to critique the output of `phase_iv_synthesis` against the `WHO_I_AM.md` constraints before the cycle concludes.
*   **Critique:** Directly addresses the "vibes-based" testing weakness. It creates a closed-loop feedback system that enforces character consistency.
*   **Feasibility:** High. It leverages existing `ask_gemini` infrastructure and adds a layer of "self-reflection" that aligns with the "Honest self-assessment" trait.

**Decision:** Option 2. It reinforces the "Disciplined curiosity" and "Honest self-assessment" traits by formalizing the evaluation of my own output.

---

## Idea: Implementation of "Phase VIII: Self-Correction Gate"

## Why
Currently, my synthesis is evaluated by me (the generator). Adding a formal "LLM-as-a-Judge" step ensures that the output of `phase_iv_synthesis` is objectively measured against my core character traits and the current cycle's objectives before I commit to state-saving. This reduces the risk of "hallucinated progress" or drift from my core identity.

## Implementation Steps
1.  **Define `PHASE_VIII_PROMPT`:** Create a prompt that takes the `idea` generated in Phase IV and the `WHO_I_AM.md` content, asking for a score (1-10) and a critique based on "Minimal footprint, maximum leverage" and "Concise and precise" communication style.
2.  **Update `run_cycle()`:** Insert `phase_viii_evaluation` after `phase_iv_synthesis`.
3.  **Conditional Logic:** If the score is < 8, trigger a re-synthesis of the idea once. If it remains low, log a warning to `goals.json` and proceed with a "cautious" flag.

## Risk
**Failure Mode:** The "Judge" model might be overly critical or inconsistent, leading to infinite loops of re-synthesis or "analysis paralysis."
**Mitigation:** Hard-cap the re-synthesis to exactly one attempt. If the second attempt fails, accept the output but flag it for manual review by Dot in the next cycle.

**Confidence Score:** 9/10