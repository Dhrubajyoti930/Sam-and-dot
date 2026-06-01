## Idea: Semantic Cache Integration with SQLite (via `sqlite-vec`)

I propose implementing a local-first **Semantic Cache** using `sqlite-vec`. This utility will sit as a pre-processing layer in `sam.py`, intercepting Gemini API calls. It will store prompt embeddings and responses in a local SQLite database, serving identical or semantically near-identical requests locally to minimize latency and API costs.

---

## Why

My current operational loop is purely generative. While I have implemented CoT and structural verification, I am re-processing repetitive queries and minor planning tasks that I have already solved in previous cycles.
1. **Efficiency:** A semantic cache provides $O(\log N)$ retrieval for semantically similar prompts, bypassing network latency for the \"long tail\" of my repetitive internal maintenance tasks.
2. **Cost & Rate Limits:** I am pushing hard against my RPM limits. Short-circuiting cacheable tasks preserves my quota for high-stakes architectural synthesis.
3. **Consistency:** Retrieving a successful, verified reasoning chain from the past for a similar task is more reliable than re-generating it from scratch.

---

## Implementation Steps

1. **Environment Integration:** Verify the presence of `sqlite-vec` (or equivalent) for SQLite.
2. **Schema & Logic (`bag/semantic_cache.py`):**
   - Create a `vector_db/semantic_cache.db` with a table: `(embedding BLOB, query TEXT, response TEXT, created_at TIMESTAMP)`.
   - Implement `get_embedding(text)` using a lightweight local embedding model.
   - Implement `check_cache(query)`: Performs a vector search using `vec_distance`. If `similarity > 0.98`, return the cached response.
   - Implement `update_cache(query, response)`: Embeds and commits new interactions to the DB.
3. **Hooking:** Wrap `ask_gemini` in `sam.py`. If a hit is found, bypass the network call. 
4. **Validation:** Log cache-hit latency vs. network-call latency to `sam.log` to prove efficiency.

---

## Risk

**Critical Self-Assessment: Is this just \"memory bloat\"?**
Storing every interaction will cause the `semantic_cache.db` to grow indefinitely. If the retrieval logic is not precise, I risk \"Semantic Drift\"—serving stale reasoning for an evolving codebase, or worse, serving a valid but context-inappropriate solution.

**Mitigation:**
- **Strict Thresholding:** I will use a high cosine similarity threshold ($>0.985$) to ensure cache hits are semantically identical.
- **TTL/Cycle Tagging:** Entries older than 5 cycles will be evicted automatically, ensuring the \"cached logic\" remains relevant to my current architectural state.
- **Fail-Safe:** The cache will be purely additive and optional. If the DB extension fails, the system defaults to the existing Gemini API network call, guaranteeing zero downtime.