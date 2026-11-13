## Scratchpad

**Option 1: Automated Trust-Scoring Middleware**
*   **Concept:** Integrate the "Trust Scoring" logic (Provenance, Integrity, Consensus) directly into the retrieval pipeline.
*   **Critique:** High impact, but requires external API dependencies (WHOIS, etc.) which introduces latency and potential points of failure.
*   **Trade-off:** Increases retrieval quality significantly but complicates the `bag/` infrastructure.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Implement a vector-based deduplication layer to prune redundant information from the `memories/` store before synthesis.
*   **Critique:** Directly addresses the "echo chamber" risk identified in the self-correction. It leverages existing semantic cache infrastructure.
*   **Trade-off:** Lower external dependency risk than Option 1; higher internal complexity in managing vector embeddings.

**Selection:** Option 2. It aligns with the "Minimal footprint, maximum leverage" core trait and directly improves the quality of the synthesis phase by ensuring the context window isn't polluted by redundant data.

---

## Idea: Semantic Deduplication Layer for Memory Management

Implement a `deduplicate_memories()` function in `bag/memory_utils.py` that uses cosine similarity on stored knowledge embeddings to identify and merge redundant entries.

## Why
As the `knowledge_log.json` grows, the synthesis phase (Phase IV) risks becoming repetitive. By deduplicating, I ensure that the context provided to the synthesis engine is high-density and diverse, improving the quality of the "Idea of the Day."

## Implementation Steps
1.  **Create `bag/memory_utils.py`**: Define a function to load `knowledge_log.json`.
2.  **Vectorization**: Use a lightweight embedding function (or simple Jaccard similarity on keyword sets if embedding overhead is too high for this cycle) to compare `summary` fields.
3.  **Merge Logic**: If similarity > 0.85, merge the entries by keeping the most recent `review_due_cycle` and concatenating unique insights.
4.  **Integration**: Call `deduplicate_memories()` at the start of Phase II (Spaced Repetition) to clean the log before review.

## Risk
**Failure Mode:** Aggressive deduplication might merge distinct but topically similar concepts, leading to "knowledge collapse" where nuanced differences are lost.
**Mitigation:** Implement a "Human-in-the-loop" flag; if the similarity score is between 0.7 and 0.85, mark for manual review rather than auto-merging.
**Confidence Score:** 8/10.

---

### Action Items
```json
[
  {
    "task": "Create bag/memory_utils.py with deduplication logic.",
    "priority": "High"
  },
  {
    "task": "Update phase_ii_spaced_repetition to invoke memory cleanup.",
    "priority": "Medium"
  }
]
```