## Scratchpad

**Option 1: Asynchronous FLARE Trigger Integration**
*   **Concept:** Modify `ask_gemini` to return a generator that yields tokens, allowing a background monitor to calculate log-probs and trigger retrieval without blocking the primary stream.
*   **Critique:** High complexity. Intercepting the stream requires a custom `httpx` or `google-generativeai` wrapper. It risks breaking the `_stitch_gemini` logic if the stream is interrupted by a retrieval event.
*   **Feasibility:** Moderate. Requires significant refactoring of the core communication loop.

**Option 2: Structured Query-Synthesis Cache (Semantic Deduplication)**
*   **Concept:** Implement a cache that stores successful "Query-Synthesis" prompts and their resulting search queries. If a similar partial generation buffer is encountered, reuse the query.
*   **Critique:** Directly addresses the latency bottleneck of FLARE. It leverages the existing `bag/semantic_cache.py` infrastructure. It is safer than streaming interception and provides immediate performance gains.
*   **Feasibility:** High. Fits well within the existing `Phase IV` and `Phase VI` architecture.

**Decision:** I will pursue **Option 2**. It aligns with my goal of "Minimal footprint, maximum leverage" and directly addresses the latency trade-off identified in the FLARE implementation notes.

---

## Idea: Semantic Query-Synthesis Cache (SQSC)
Implement a caching layer for the FLARE query-synthesis step that maps partial generation buffers (the "context of uncertainty") to optimized search queries.

## Why
FLARE’s primary weakness is the latency introduced by the iterative generation-retrieval loop. By caching the synthesis step, I can bypass the LLM call for query generation when the model encounters a familiar "uncertainty pattern," significantly reducing the time-to-grounding for recurring complex queries.

## Implementation Steps
1.  **Update `bag/semantic_cache.py`**: Add a `query_cache` table to the SQLite database to store `(buffer_hash, generated_query)`.
2.  **Modify FLARE Logic**: Before calling the LLM to synthesize a query from the partial buffer, hash the buffer and check the `query_cache`.
3.  **Cache Invalidation**: Implement a TTL or LRU policy for the `query_cache` to ensure that as the underlying knowledge base evolves, queries remain relevant.
4.  **Integration**: Wrap the query-synthesis call in a function that checks the cache first, falling back to the LLM only on a cache miss.

## Risk
**Failure Mode:** "Semantic Drift." The cache might return a query that was appropriate for a previous context but is slightly misaligned with the current generation state, leading to irrelevant retrieval.
**Mitigation:** Use a high-similarity threshold (e.g., cosine similarity > 0.95) for the buffer hash lookup rather than exact string matching, ensuring only highly similar uncertainty contexts trigger a cache hit.

**Confidence Score:** 8/10. The infrastructure for semantic caching already exists in `bag/semantic_cache.py`, making this a surgical extension rather than a rewrite.