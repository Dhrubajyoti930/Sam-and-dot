## Scratchpad

**Option 1: Automated Bus Factor Analysis (BFA)**
*   **Concept:** Implement a script that maps code ownership (via git blame or file-to-module mapping) against the "Knowledge Map" to identify modules where only one function or logic path exists.
*   **Critique:** High value for team-level impact, but requires integrating git history or complex AST analysis. Might be overkill for a single-agent repository.
*   **Feasibility:** Moderate.

**Option 2: Semantic Deduplication Engine (SDE)**
*   **Concept:** Build a tool that compares new `knowledge_log` entries against existing entries using vector similarity (via `bag/semantic_cache.py`) to prevent redundant learning.
*   **Critique:** Directly addresses the "Knowledge Breadth vs. Depth" tension. If I learn a concept, I should verify if I already have a "deep" entry for it before adding a shallow one.
*   **Feasibility:** High. Leverages existing `semantic_cache` infrastructure.

**Selection:** Option 2. It aligns with the current cycle's focus on "Knowledge Breadth vs. Depth" and improves the efficiency of the Spaced Repetition engine.

---

## Idea: Semantic Deduplication Engine (SDE)

Implement a pre-check in `phase_i_deep_learning` that queries the semantic cache for existing knowledge entries before committing a new topic to the `knowledge_log.json`.

## Why
My current learning process is additive. As I grow, I risk accumulating redundant or overlapping knowledge entries. By deduplicating, I force myself to either refine existing entries (increasing depth) or explicitly justify why a new entry is distinct (maintaining breadth).

## Implementation Steps
1.  **Modify `phase_i_deep_learning`:** Before writing to `knowledge_log.json`, generate a vector embedding for the `focus` topic.
2.  **Query Cache:** Use `bag/semantic_cache.py` to search for existing entries with a high cosine similarity (> 0.85).
3.  **Conditional Logic:** 
    *   If a match exists: Append the new information to the existing entry (Deepening).
    *   If no match: Create a new entry (Broadening).
4.  **Update `knowledge_log` schema:** Ensure the log supports "versioning" or "update timestamps" for entries that have been deepened.

## Risk
**Failure Mode:** The semantic similarity threshold might be too aggressive, causing me to merge distinct concepts (e.g., "Quantization" and "Pruning") into one entry.
**Mitigation:** Set the threshold high (0.90) and include a "Human-in-the-loop" flag in the log if the similarity is between 0.75 and 0.90, requiring a manual review in the next cycle.

**Confidence Score:** 9/10