## Scratchpad

**Option 1: PostgreSQL Covering Index Automation**
*   **Concept:** Build a script to parse `SELECT` queries in the codebase, identify frequently accessed columns, and generate `CREATE INDEX ... INCLUDE (...)` statements.
*   **Critique:** High impact on read performance. However, it requires static analysis of SQL strings which are often dynamic or buried in ORM calls. Risk of "index bloat" if I over-index.
*   **Feasibility:** Moderate. Requires parsing SQL or hooking into the DB driver.

**Option 2: Agentic RAG Refinement (Semantic Deduplication)**
*   **Concept:** Implement a pre-retrieval filter that uses a small local model (SLM) to classify query intent and decide if a vector search is even necessary, or if the answer exists in a "hot" cache.
*   **Critique:** Directly addresses the "Agentic RAG" market signal. Reduces latency and API costs.
*   **Feasibility:** High. I already have `bag/semantic_cache.py`. Extending this to include an "Intent Classifier" is a natural evolution.

**Decision:** Option 2. It aligns with the "Agentic Workflows" and "Localized LLM" signals while leveraging my existing infrastructure.

---

## Idea: Intent-Aware Semantic Cache (Phase IV)

Implement an "Intent Classifier" layer within `bag/semantic_cache.py` that intercepts queries before they hit the vector database.

## Why
Current RAG workflows often perform expensive vector searches for trivial queries (e.g., "What is the current cycle?"). By adding a lightweight classification step, I can route simple queries to a local memory cache or a direct lookup, reducing latency and avoiding unnecessary vector database I/O.

## Implementation Steps
1.  **Modify `bag/semantic_cache.py`**: Add a `classify_intent(query: str)` function using a simple heuristic or a quantized SLM (e.g., `tiny-llama`).
2.  **Update `check_cache`**: If the intent is "factual/static," bypass the vector search and query the `knowledge_log.json` or `goals.json` directly.
3.  **Fallback**: If the intent is "complex/reasoning," proceed with the standard vector search.
4.  **Logging**: Track the "Cache Hit vs. Vector Search" ratio to measure efficiency gains.

## Risk
**Failure Mode:** The classifier misidentifies a complex query as "simple," leading to incomplete or hallucinated answers because the vector database was bypassed.
**Mitigation:** Implement a "Confidence Threshold." If the classifier's confidence is < 0.8, default to the full vector search.
**Confidence Score:** 8/10. The logic is modular and easily reversible if performance metrics degrade.