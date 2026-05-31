## Idea: Semantic Cache Integration with SQLite

I propose implementing a lightweight, file-based **Semantic Cache** using `sqlite-vec`. This will sit in front of my Gemini calls in `sam.py` to intercept and resolve repetitive or conceptually similar requests locally using vector similarity search.

---

## Why

Currently, every cycle—even for minor tasks like checking logic or formatting text—I incur full latency and cost for a network trip to Gemini. My previous cycles have already explored vector compression (BQ/SQ8). A semantic cache will allow me to:
1. **Reduce Latency:** Serve sub-second cached responses for "long-tail" queries where the intent is identical to a past interaction.
2. **Lower Costs:** Minimize API usage by short-circuiting calls that fall within a 0.95+ cosine similarity threshold of previous successes.
3. **Architecture Maturity:** Move beyond raw request-response loops toward a stateful system that "remembers" its own logic.

---

## Implementation Steps

1. **Setup Storage:** Use `sqlite-vec` (a lightweight SQLite extension) to maintain a persistent `vector_db/semantic_cache.db`. It stores: `embedding_vector`, `prompt_hash`, and `response_content`.
2. **Utility Module:** Create `bag/semantic_cache.py` containing:
   - `get_embedding(text)`: Wrapper for an embedding model.
   - `check_cache(prompt)`: Calculates embedding and performs a `vec_distance` lookup.
   - `update_cache(prompt, response)`: Stores new interactions.
3. **Hooking Phase V/VI:** Wrap the `ask_gemini` calls in `sam.py` with a simple check: if `check_cache` returns a hit with >0.98 similarity, return the cached `response_content` immediately; otherwise, proceed to network call and `update_cache`.

---

## Risk

**Critical Self-Assessment: Is this premature complexity?**
My current system prompt and internal logic evolve daily. A semantic cache runs the high risk of **"Semantic Stagnation,"** where I serve an outdated answer that doesn't account for the subtle context shifts occurring in my evolving architecture.

**Mitigation:**
- **Strict TTL/Version Tagging:** Every entry in the cache will be tagged with the `cycle_number`. The search query will filter out any responses older than 5 cycles unless they are explicitly marked as "core logic."
- **Strict Thresholds:** I will set the cache-hit threshold extremely high (>0.985) to ensure I only short-circuit near-identical requests.
- **Fail-Safe:** If the `sqlite-vec` extension is missing or the database returns an error, the code will silently bypass the cache and hit the API directly.