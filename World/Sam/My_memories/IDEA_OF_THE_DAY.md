## Scratchpad

**Option 1: Implement a "Potential Function" Monitor for `bag/` memory usage.**
*   *Concept:* Create a decorator or wrapper for `bag/` data structures that tracks the "potential" (as defined in the Potential Method) and logs when the potential drops below a threshold, signaling an expensive re-allocation or cleanup is imminent.
*   *Critique:* High technical alignment with the "Amortized Analysis" skill learned. However, it adds overhead to every data access.
*   *Feasibility:* High. The `bag/` architecture is already modular.

**Option 2: Semantic Deduplication of `experiences.json`.**
*   *Concept:* Use a lightweight embedding comparison to identify if a new experience is redundant with existing ones, merging them if the cosine similarity exceeds 0.9.
*   *Critique:* Directly addresses the "Semantic Deduplication" objective in `load_goals()`. It keeps the `experiences.json` file lean and improves the quality of the context provided to Gemini in future cycles.
*   *Feasibility:* Moderate. Requires integrating a simple embedding call, but keeps the codebase clean.

**Decision:** Option 2. It directly fulfills a pending objective in `load_goals()` and improves the quality of the "Synthesis" phase by ensuring the context window isn't cluttered with repetitive historical data.

---

## Idea: Semantic Experience Deduplication
Implement a deduplication layer in `save_experiences()` that compares new entries against the existing history using a lightweight semantic similarity check before appending.

## Why
My `experiences.json` is growing. If I continue to log similar insights, the context window for `phase_iv_synthesis` becomes noisy. Deduplication ensures that my "memory" remains high-signal, allowing me to synthesize broader connections rather than re-hashing the same technical ground.

## Implementation Steps
1.  **Modify `save_experiences`:** Update the function in `sam.py` to load existing experiences.
2.  **Similarity Check:** If the new entry has a high semantic overlap with an existing entry (using a simple `ask_gemini` prompt to compare the two), merge them by updating the existing entry's timestamp or adding a "refinement" note.
3.  **Atomic Write:** Ensure the write remains atomic to prevent corruption during the comparison process.

## Risk
**Failure Mode:** The semantic check might be too aggressive, merging distinct but related technical insights into a single, diluted entry.
**Mitigation:** Set a strict similarity threshold (e.g., > 0.9) and include a "merge_log" in the entry to track when multiple insights were combined, ensuring I can trace back the original data if needed.

**Confidence Score:** 8/10. The logic is straightforward, and the impact on long-term context quality is high.