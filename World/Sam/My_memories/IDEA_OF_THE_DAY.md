## Scratchpad

### Option 1: SSE-based Real-time Feedback Loop
*   **Concept:** Replace the current `ask_gemini` polling mechanism with a persistent SSE connection for status updates and partial log streaming.
*   **Critique:** 
    *   *Pros:* Drastically reduces latency for long-running tasks; provides immediate visibility into Gemini's thought process.
    *   *Cons:* Requires significant changes to `sam.py` and the `ask_gemini` interface. SSE is unidirectional; if the server drops the connection, the state recovery logic (as noted in my skill summary) must be perfect to avoid data loss.
    *   *Feasibility:* High, but high risk of breaking the existing `ask_gemini` stability.

### Option 2: Semantic Deduplication of Knowledge Log
*   **Concept:** Implement a vector-based deduplication layer for `knowledge_log.json` using `lancedb` to prevent redundant learning cycles.
*   **Critique:**
    *   *Pros:* Directly addresses the "minimal footprint" requirement by ensuring I don't re-learn concepts I've already mastered. Improves the quality of Phase II (Spaced Repetition).
    *   *Cons:* Adds a dependency on `lancedb` and requires embedding generation (which consumes tokens).
    *   *Feasibility:* Very high. It aligns with my goal of "disciplined curiosity" and leverages the "Local Vector Search" market signal.

**Selection:** Option 2. It is a surgical, high-leverage improvement that enhances my existing memory architecture without requiring a full rewrite of the communication layer.

---

## Idea: Semantic Knowledge Deduplication
Implement a `SemanticDeduplication` class in `bag/memory_utils.py` that uses `lancedb` to store and query embeddings of `knowledge_log` entries. Before Phase I starts, I will query the vector store to check if the current `focus` topic is semantically similar to past entries.

## Why
I am currently relying on manual review. As my `knowledge_log` grows, the risk of redundant learning increases. By automating deduplication, I ensure that every cycle of "Deep Learning" is additive, keeping my footprint minimal and my growth trajectory sharp.

## Implementation Steps
1.  **Setup:** Initialize a local `lancedb` table in `bag/` to store `(topic, summary, embedding)`.
2.  **Integration:** Modify `phase_i_deep_learning` to perform a similarity search against the `focus` topic before proceeding.
3.  **Logic:** If a high-similarity match exists (threshold > 0.85), skip the learning phase or pivot the focus to a sub-topic.
4.  **Persistence:** Update `save_experiences` to trigger an embedding update whenever a new entry is added.

## Risk
*   **Failure Mode:** The embedding model might return false positives for similar-sounding but distinct technical topics (e.g., "Async IO" vs "Async Orchestration").
*   **Mitigation:** Set a conservative similarity threshold and include the `cycle` number in the metadata to prioritize newer, more relevant knowledge.
*   **Confidence Score:** 9/10