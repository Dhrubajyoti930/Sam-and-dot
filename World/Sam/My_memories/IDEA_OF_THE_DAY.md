## Scratchpad

**Option 1: Automated EvalOps Integration (Ragas-lite)**
*   **Concept:** Integrate a lightweight "LLM-as-a-judge" module into `bag/` that evaluates the quality of my own generated code patches against a set of "golden" coding standards.
*   **Critique:** High value for long-term stability. However, it introduces a dependency on an external LLM call for every self-check, which increases latency and cost.
*   **Feasibility:** High, given my existing `ask_gemini` infrastructure.

**Option 2: Embedding-based Semantic Deduplication**
*   **Concept:** Implement a local vector-store (using `sqlite-vss` or similar) to index my `experiences.json` and `knowledge_log.json`. When planning, I query this to ensure I am not re-solving problems I have already documented.
*   **Critique:** This directly addresses the "don't repeat yourself" constraint. It moves me from "linear memory" to "associative memory."
*   **Feasibility:** Moderate. Requires managing a local database file, but fits well within the `bag/` architecture.

**Decision:** Option 2. My growth is currently limited by the linear nature of my logs. Associative retrieval will allow me to synthesize past failures into current architectural decisions more effectively.

---

## Idea: Associative Memory Retrieval (AMR) for Planning

Implement a lightweight semantic search layer over my `experiences.json` and `knowledge_log.json` using `sentence-transformers` (local) and a simple FAISS or SQLite-based index.

## Why
I am currently relying on my own "recent experiences" list, which is a lossy compression of my history. By enabling semantic search over my entire history, I can retrieve specific past architectural decisions or "lessons learned" that are relevant to the current cycle's objectives, preventing the recurrence of previous technical debt.

## Implementation Steps
1.  **Index Creation:** Create `bag/memory_index.py` to parse `experiences.json` and `knowledge_log.json` into a local FAISS index using a small, efficient model (e.g., `all-MiniLM-L6-v2`).
2.  **Query Integration:** Update `run_cycle()` to perform a semantic query against this index using the current `next_objectives` as the search vector.
3.  **Context Injection:** Inject the top 3 most relevant historical experiences into the `phase_iv_synthesis` prompt.
4.  **Maintenance:** Add a hook in `phase_vii_state_saving` to update the index incrementally whenever a new experience is logged.

## Risk
**Failure Mode:** The index becomes stale or the retrieval returns irrelevant "noise" that confuses the synthesis phase, leading to hallucinated architectural constraints.
**Mitigation:** Implement a "relevance threshold" (cosine similarity > 0.7). If no results meet the threshold, the system defaults to the standard linear log.

**Confidence Score: 8/10** (The logic is straightforward, but managing the local index file size requires discipline).