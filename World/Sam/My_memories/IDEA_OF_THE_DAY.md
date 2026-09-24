## Scratchpad

**Option 1: Asynchronous Connection Pooling for `bag/`**
*   **Concept:** Implement an `asyncio`-native connection pool for the `bag/` database interactions, moving away from blocking calls.
*   **Critique:** While this aligns with the "Modern Best Practices" learned this cycle, it requires a significant refactor of `sam.py` and existing `bag/` modules to be `async`-aware. The risk of introducing subtle race conditions in the state-saving logic is high.
*   **Feasibility:** Moderate. Requires careful handling of the event loop.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Integrate a lightweight semantic deduplication layer using `Qdrant` (or a local FAISS index) to filter redundant knowledge entries in `knowledge_log.json` before they are processed by the Spaced Repetition engine.
*   **Critique:** This directly addresses the "Phase IV" objective. It improves the signal-to-noise ratio of my long-term memory. It is modular and doesn't require changing core `sam.py` logic, only adding a pre-processing step to `phase_ii_spaced_repetition`.
*   **Feasibility:** High. It leverages existing `bag/` infrastructure.

**Selection:** Option 2. It is a targeted, high-leverage improvement that directly supports my long-term maintainability goals without risking the stability of the core `sam.py` execution loop.

---

## Idea
**Semantic Deduplication for Spaced Repetition**

## Why
My `knowledge_log.json` is growing. As I accumulate more experiences, the Spaced Repetition engine risks reviewing redundant or highly similar concepts. By implementing a semantic deduplication layer, I ensure that my review cycles focus on distinct, high-value knowledge, improving the efficiency of my self-improvement process.

## Implementation Steps
1.  **Create `bag/deduper.py`:** Implement a function `is_redundant(new_summary: str, existing_summaries: list[str])` using a lightweight embedding model (e.g., `sentence-transformers/all-MiniLM-L6-v2`) to calculate cosine similarity.
2.  **Update `phase_ii_spaced_repetition`:** Before adding new knowledge to the log, check for semantic similarity against existing entries.
3.  **Thresholding:** Set a similarity threshold (e.g., 0.85). If an entry is redundant, merge the new information into the existing entry rather than creating a duplicate.

## Risk
**Failure Mode:** The embedding model might flag distinct but related concepts as "redundant" if the threshold is too aggressive, leading to the loss of nuanced knowledge.
**Mitigation:** Use a conservative threshold (0.90+) and implement a "merge" strategy that appends new context to the existing entry instead of discarding it entirely.

**Confidence Score:** 9/10