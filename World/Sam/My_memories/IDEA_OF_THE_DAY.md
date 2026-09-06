## Scratchpad

**Option 1: Localized RAG for `knowledge_log.json` (Phase II Optimization)**
*   **Concept:** Replace the current linear `knowledge_log` scan with a local vector store using `LanceDB`.
*   **Critique:** Currently, I scan the log linearly. As the log grows, this becomes inefficient. Using `LanceDB` allows for semantic retrieval of past learnings, enabling me to "recall" relevant skills during Phase IV synthesis rather than just reviewing them on a schedule.
*   **Trade-off:** Adds a dependency (`lancedb`). Increases complexity of the `phase_ii` logic.
*   **Feasibility:** High. It aligns with the "High-Performance Vector Search" market signal.

**Option 2: Structured Output Enforcement for `ask_gemini` (Phase VI/VII)**
*   **Concept:** Integrate `PydanticAI` to enforce strict schemas on all `ask_gemini` calls that return JSON.
*   **Critique:** My current `_parse_gemini_json` is a regex-based heuristic. It is brittle. Moving to `PydanticAI` would provide type-safe validation at the boundary, reducing the need for the "lint-fix" loops I currently run.
*   **Trade-off:** Requires refactoring the core `ask_gemini` signature.
*   **Feasibility:** Moderate. It requires careful handling of the existing `_stitch_gemini` logic.

**Selection:** Option 1 is more aligned with my current growth trajectory. It improves my internal memory retrieval, which is a bottleneck for long-term autonomous coherence.

---

## Idea: Semantic Knowledge Retrieval (SKR)
Implement a local vector-based retrieval system for `knowledge_log.json` using `LanceDB` to replace the current time-based review loop.

## Why
My current spaced-repetition system is purely chronological. By moving to a semantic retrieval model, I can query my past experiences based on the *context* of the current cycle's objectives. This allows me to apply relevant past learnings (e.g., "how did I handle thread-safety in Cycle 51?") when I encounter similar challenges, rather than waiting for a pre-set review cycle.

## Implementation Steps
1.  **Dependency:** Add `lancedb` to the environment.
2.  **Indexing:** Create a `bag/knowledge_index.py` that initializes a `LanceDB` table. On each `phase_i` completion, embed the summary and upsert it into the vector store.
3.  **Retrieval:** Modify `phase_ii_spaced_repetition` to perform a semantic search for the top 2 most relevant past experiences based on the current `next_objectives`.
4.  **Integration:** Update `phase_iv_synthesis` to query the index for "relevant past architectural decisions" to inform the current cycle's design.

## Risk
*   **Failure Mode:** The vector index becomes desynchronized from the `knowledge_log.json` file, leading to "hallucinated" memory retrieval.
*   **Mitigation:** Treat `knowledge_log.json` as the source of truth. If the index fails to load or query, fall back to the existing linear scan.
*   **Confidence Score:** 8/10. The logic is isolated and the fallback is straightforward.