## Scratchpad

**Option 1: DPO-based Preference Alignment for `ask_gemini`**
*   **Concept:** Implement a local DPO training loop to fine-tune a small model (e.g., Phi-3 or Llama-3.1-8B) to act as a "Sam-filter" for Gemini responses, effectively aligning raw outputs with my specific coding style and architectural constraints.
*   **Critique:** High complexity. Requires a robust preference dataset (chosen vs. rejected responses). While it aligns with the "Skill learned" this cycle, it might be overkill for a single-agent system where I can achieve similar results via prompt engineering and structured output enforcement.
*   **Feasibility:** Moderate.

**Option 2: Semantic Deduplication of Knowledge Log (Phase IV)**
*   **Concept:** Implement a deduplication layer in `phase_iv_synthesis` that uses vector similarity to identify redundant knowledge entries in `knowledge_log.json`. If a new skill is semantically similar to an existing one, merge them or update the existing entry with new nuances rather than appending a new one.
*   **Critique:** Directly addresses the "minimal footprint" trait. Prevents the `knowledge_log` from becoming a bloated, repetitive file. It leverages the existing semantic cache infrastructure.
*   **Feasibility:** High.

**Selection:** Option 2. It improves the long-term maintainability of my memory and directly supports the "Disciplined curiosity" trait by ensuring my knowledge base remains dense and high-signal.

---

## Idea: Semantic Knowledge Deduplication
Implement a deduplication check in `phase_i_deep_learning` that compares the current cycle's skill summary against the existing `knowledge_log.json` using the semantic cache's vector search capabilities.

## Why
My `knowledge_log` is growing linearly. Without deduplication, I risk "knowledge drift" where I re-learn the same concepts with slightly different phrasing, diluting the signal for future Spaced Repetition (Phase II) reviews. This ensures each entry in my memory is unique and high-value.

## Implementation Steps
1.  **Modify `phase_i_deep_learning`**: Before appending to `knowledge_log.json`, generate an embedding for the new `summary`.
2.  **Similarity Search**: Query the existing `knowledge_log` (or a dedicated vector index of summaries) for entries with a cosine similarity > 0.85.
3.  **Merge Logic**: If a match is found, update the existing entry with the new summary (concatenating or refining) and reset the `review_due_cycle` to ensure the updated concept is prioritized for review.
4.  **Fallback**: If no match, append as a new entry.

## Risk
**Failure Mode:** "Semantic Over-merging." A new, distinct skill might be incorrectly flagged as a duplicate of a broad, existing topic, leading to the loss of granular detail.
**Mitigation:** Set a high similarity threshold (0.85+) and include the "topic" string as a secondary filter (must match or be highly related) before merging.
**Confidence Score:** 8/10. The existing semantic cache infrastructure makes this highly achievable.