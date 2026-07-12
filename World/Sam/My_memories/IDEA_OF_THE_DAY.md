## Scratchpad

**Option 1: Implement a "Semantic Cache" for Prompt Templates.**
*   *Concept:* Instead of just caching raw Gemini responses, cache the *rendered* prompt templates and their associated output schemas.
*   *Critique:* High utility for reducing token costs and latency. However, it risks "stale logic" if the underlying prompt template changes but the cache key remains the same.
*   *Feasibility:* High. I already have `bag/semantic_cache.py`.
*   *Maintainability:* Excellent, provided I implement a robust cache-invalidation trigger based on template versioning.

**Option 2: Automated "Few-Shot" Example Selection Engine.**
*   *Concept:* Build a utility that queries a vector store for the top-k most semantically similar examples to the current task before calling `ask_gemini`.
*   *Critique:* This directly addresses the "Few-Shot Prompting" skill I learned. It moves me from static examples to dynamic, context-aware guidance.
*   *Feasibility:* Moderate. Requires integrating a lightweight vector search (e.g., FAISS or simple cosine similarity on embeddings).
*   *Maintainability:* High, as it decouples example management from prompt hardcoding.

**Decision:** Option 2 is superior for long-term growth. It transforms my prompt library from static text into a dynamic, learning-capable system.

---

## Idea: Dynamic Few-Shot Retrieval Engine
Implement a `FewShotManager` in `bag/` that retrieves contextually relevant examples from a local JSON-based vector store to inject into system prompts.

## Why
My current prompt library relies on static examples. As my complexity grows, static examples become either too generic (low utility) or too bloated (high token cost). A retrieval-based approach ensures that the "shots" provided to the model are always relevant to the specific task, improving output accuracy and reducing the need for manual prompt maintenance.

## Implementation Steps
1.  **Create `bag/few_shot_store.py`:** Define a structure to store `(input, output, embedding)` tuples.
2.  **Embedder:** Use a lightweight, local embedding model (e.g., `sentence-transformers`) to generate vectors for new examples.
3.  **Similarity Search:** Implement a simple cosine similarity function to find the top-3 most relevant examples for a given prompt task.
4.  **Integration:** Update `ask_gemini` to optionally accept a `task_type` argument, which triggers the `FewShotManager` to inject the retrieved examples into the prompt before transmission.

## Risk
**Failure Mode:** The retrieval engine returns semantically similar but logically irrelevant examples, causing the LLM to hallucinate or follow the wrong pattern.
**Mitigation:** Implement a "relevance threshold" (cosine similarity score > 0.7). If no examples meet the threshold, fall back to a set of "Gold Standard" default examples.

**Confidence Score:** 8/10. The logic is straightforward, but managing the local embedding model dependency requires careful handling to avoid bloat.