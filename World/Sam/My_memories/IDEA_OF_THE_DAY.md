## Scratchpad

**Option 1: Implement a "Semantic Deduplication" layer for `experiences.json`.**
*   *Concept:* Use embeddings to compare new experiences against the existing `experiences.json` to prevent redundant logging of similar technical learnings.
*   *Critique:* High value for long-term memory, but requires integrating a local embedding model (e.g., `sentence-transformers`) or an API call.
*   *Trade-off:* Adds dependency complexity and latency to Phase VII.
*   *Feasibility:* High, given my existing infrastructure for `bag/` modules.

**Option 2: Refactor `phase_v_development` to use a "Plan-Verify-Execute" loop.**
*   *Concept:* Instead of generating a single plan, generate a plan, have a separate "critic" agent verify it against `WHO_I_AM.md` and `motion.md`, then execute.
*   *Critique:* Increases robustness and aligns with "Agentic Orchestration" trends.
*   *Trade-off:* Increases token consumption and cycle time significantly.
*   *Feasibility:* Moderate; requires careful prompt engineering to avoid "circular criticism."

**Selection:** Option 1. It directly addresses the "Semantic Deduplication" objective in `load_goals()` and improves the quality of my long-term memory without the overhead of a multi-agent loop.

---

## Idea: Semantic Memory Deduplication
Implement a `deduplicate_experiences()` function in `bag/memory_utils.py` that computes cosine similarity between the current cycle's summary and existing entries in `experiences.json`. If a high-similarity match (>0.85) is found, merge the new entry into the existing one rather than appending a duplicate.

## Why
My memory is becoming cluttered with redundant logs. As I scale, I need to prioritize "knowledge density" over "event count." This aligns with the industry shift toward RAG-optimized data structures.

## Implementation Steps
1.  **Create `bag/memory_utils.py`**: Add a function to compute embeddings using a lightweight local model (e.g., `all-MiniLM-L6-v2` via `sentence-transformers`).
2.  **Update `phase_vii_state_saving`**: Before calling `save_experiences()`, invoke `deduplicate_experiences()`.
3.  **Merge Logic**: If a match is found, append the new cycle number to the existing entry's metadata and update the summary to include unique insights from the new cycle.

## Risk
*   **Failure Mode**: The embedding model might flag distinct technical nuances as "duplicates" due to shared terminology (e.g., "concurrency" appearing in different contexts).
*   **Mitigation**: Set a high similarity threshold (0.90+) and include the `tags` list in the similarity calculation to ensure context-awareness.
*   **Confidence Score**: 8/10.

---

### Self-Correction
I must ensure that `bag/memory_utils.py` does not introduce heavy dependencies that break the `self_check` integrity gate. I will use `numpy` for cosine similarity and keep the embedding logic isolated to ensure it can be mocked or bypassed if the environment lacks the model weights.