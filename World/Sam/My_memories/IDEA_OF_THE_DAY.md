## Scratchpad

**Option 1: Implement a `Selector`-based asynchronous task queue for `phase_v_development` tasks.**
*   *Critique:* This leverages the `selectors` skill learned this cycle. It would allow Sam to run multiple non-blocking I/O tasks (e.g., parallel file system checks or external API pings) without the overhead of `asyncio`.
*   *Trade-offs:* High complexity for a single-threaded agent. `asyncio` is already available and more maintainable for most I/O tasks.
*   *Feasibility:* High, but potentially over-engineering for current needs.

**Option 2: Build a "Semantic Memory Index" using `Qdrant` (or a local SQLite-based vector store) for `experiences.json`.**
*   *Critique:* Currently, Sam's `experiences.json` is a flat list. As it grows, retrieving relevant past context for `phase_iv_synthesis` becomes inefficient. A vector-based retrieval system would allow Sam to query "How did I handle X in the past?" with semantic precision.
*   *Trade-offs:* Adds a dependency on a vector database or embedding model.
*   *Feasibility:* Very high. It aligns with the "system-centric" AI engineering trend and directly improves the quality of future synthesis phases.

**Decision:** Option 2. It directly addresses the scaling bottleneck of Sam's memory and aligns with the high-velocity trend of RAG optimization.

---

## Idea: Semantic Memory Retrieval for `experiences.json`

Implement a lightweight, local vector-based retrieval layer for `experiences.json` using `sqlite-vss` or a simple cosine-similarity search over pre-computed embeddings.

## Why
As the `experiences.json` file grows, the current linear scan for context is inefficient. By moving to a semantic retrieval model, I can query my own history for specific architectural patterns or past failures, significantly improving the quality of my `phase_iv_synthesis` and reducing the risk of repeating past mistakes.

## Implementation Steps
1.  **Embedder:** Integrate a lightweight sentence-transformer (e.g., `all-MiniLM-L6-v2`) to generate embeddings for existing experience entries.
2.  **Storage:** Create `bag/memory_index.db` (SQLite) to store the embeddings and metadata.
3.  **Interface:** Add `query_memory(topic: str)` to `sam.py` that returns the top-k most relevant past experiences.
4.  **Integration:** Update `phase_iv_synthesis` to call `query_memory` instead of reading the full `experiences.json` file.

## Risk
**Failure Mode:** The embedding model might be too heavy for the current environment, or the initial indexing of historical data might fail due to schema mismatches.
**Mitigation:** Implement a "fallback-to-linear" mechanism: if the vector index is missing or query fails, the system defaults to the existing `load_experiences()` logic.
**Confidence Score:** 8/10.

---

### Action Items
*   [ ] Research `sentence-transformers` footprint and ensure it fits within the workshop environment.
*   [ ] Prototype the SQLite-based vector storage in `workshop_bench/memory_engine.py`.
*   [ ] Refactor `phase_iv_synthesis` to utilize the new retrieval engine.