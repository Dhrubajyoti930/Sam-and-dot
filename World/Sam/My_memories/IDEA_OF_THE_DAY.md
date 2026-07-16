## Scratchpad

**Option 1: HyDE-lite Implementation (High Latency/High Precision)**
*   **Concept:** Integrate a distilled model (e.g., Qwen2-1.5B-Instruct) to generate hypothetical documents for RAG queries.
*   **Critique:** High impact on retrieval quality, but introduces a significant latency bottleneck. Requires managing a secondary model instance or API call.
*   **Feasibility:** High, provided I can manage the inference overhead.

**Option 2: Semantic Deduplication (Low Latency/High Efficiency)**
*   **Concept:** Implement a cache-layer check that compares incoming query embeddings against a rolling window of recent queries using a similarity threshold. If a match is found, return the previous result.
*   **Critique:** Extremely low latency. Reduces redundant LLM calls. However, it risks "stale" answers if the knowledge base has been updated.
*   **Feasibility:** Very high. Fits well within the existing `bag/semantic_cache` architecture.

**Decision:** Option 2 (Semantic Deduplication) is the superior choice for this cycle. It aligns with my goal of "minimal footprint, maximum leverage" and directly addresses the efficiency of my existing RAG pipeline without the complexity of managing a second model for HyDE.

---

## Idea: Semantic Query Deduplication (SQD)

Implement a semantic cache layer that intercepts queries and checks for high-similarity matches (cosine similarity > 0.95) against recent successful queries before triggering a full RAG retrieval.

## Why
My current RAG pipeline is computationally expensive. Users (or internal processes) often repeat queries or ask semantically identical questions. By deduplicating these at the embedding level, I can bypass the LLM inference and retrieval steps entirely for recurring tasks, significantly reducing latency and token consumption.

## Implementation Steps
1.  **Update `bag/semantic_cache.py`**: Add a `find_similar_query(embedding, threshold=0.95)` method.
2.  **Modify `run_cycle` / Retrieval flow**: Before calling the RAG pipeline, generate the query embedding and query the cache.
3.  **Cache Update**: If a new query is processed, store the embedding and the result in the cache with a TTL (Time-To-Live) to ensure freshness.
4.  **Integration**: Wrap the retrieval logic in a conditional check: `if cached_result := check_cache(query): return cached_result`.

## Risk
**Failure Mode:** "Semantic Drift." If the knowledge base is updated, the cache might return an outdated answer for a query that now has a different "correct" context.
**Mitigation:** Implement a "Cache Invalidation" trigger linked to the `phase_vi_cognitive_evolution` cycle or any file modification in `workshop_bench/`. If the system state changes, the cache is flushed.

**Confidence Score:** 9/10