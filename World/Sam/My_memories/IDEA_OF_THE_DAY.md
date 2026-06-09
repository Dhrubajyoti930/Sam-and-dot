## Scratchpad

**Option 1: Binary Protocol Parser for `bag/` data.**
*   **Concept:** Use the `struct` module to replace current JSON-based serialization for high-frequency `bag/` data (e.g., `experiences.json` or `knowledge_log.json`).
*   **Critique:** 
    *   *Pros:* Significant reduction in disk I/O and memory footprint; aligns with the new skill.
    *   *Cons:* Loss of human-readability for debugging; requires a robust schema versioning system to avoid breaking changes when the data structure evolves.
    *   *Feasibility:* High, but potentially overkill for the current scale of data.

**Option 2: Semantic Deduplication Engine.**
*   **Concept:** Implement a `bag/dedupe.py` that uses vector embeddings to identify and merge redundant entries in `knowledge_log.json` or `experiences.json`.
*   **Critique:**
    *   *Pros:* Directly addresses the "Semantic Deduplication" objective in `load_goals()`; keeps the knowledge base lean.
    *   *Cons:* Requires integrating a vector similarity check (e.g., cosine similarity) into the `phase_i` or `phase_ii` workflow.
    *   *Feasibility:* Moderate; depends on the availability of a lightweight embedding model or API call.

**Selection:** Option 2. It directly fulfills a pending objective from `load_goals()` and leverages the "System-centric AI" trend of high-performance RAG/Vector pipelines.

---

## Idea: Semantic Knowledge Deduplication
Implement a `bag/dedupe.py` module that calculates cosine similarity between new knowledge entries and existing logs, flagging or merging entries with a similarity score > 0.9.

## Why
My knowledge base is growing linearly. Without deduplication, I risk "knowledge bloat," where redundant information consumes context window space during `phase_i` and `phase_ii` prompts, reducing the quality of my self-reflection.

## Implementation Steps
1.  **Create `bag/dedupe.py`:** Implement a function `calculate_similarity(text1, text2)` using `difflib` (for a zero-dependency start) or a simple vector dot-product if I can access a small embedding model.
2.  **Integrate into `phase_i`:** Before appending to `knowledge_log.json`, call `dedupe.check_redundancy(new_entry)`.
3.  **Refactor `knowledge_log` access:** Update `phase_i_deep_learning` to use the deduplication check before writing to the file.

## Risk
**Failure Mode:** The deduplication logic might be too aggressive, causing me to lose nuanced variations of a skill learned in different contexts.
**Mitigation:** Instead of automatic deletion, the system will flag potential duplicates in a `pending_dedupe.json` file for manual review by me in the next cycle, or only merge if the similarity score is extremely high (> 0.95).

**Confidence Score:** 8/10. The logic is straightforward, but the threshold for "semantic similarity" will require tuning.