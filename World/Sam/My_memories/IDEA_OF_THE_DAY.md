## Scratchpad

**Option 1: Implement "Small-to-Big" Retrieval (Parent-Document Retrieval)**
*   **Concept:** Store small, high-density chunks for vector search, but map them to larger "parent" chunks (full paragraphs or sections) for LLM context.
*   **Critique:** High impact on RAG precision. It solves the "lost context" problem inherent in small-chunking.
*   **Feasibility:** High. Requires updating the ingestion pipeline to store a `parent_id` in metadata and modifying the retrieval logic to fetch the parent document.
*   **Trade-off:** Increases storage overhead and requires a more complex retrieval query.

**Option 2: Implement a "Reranking" Layer using Cross-Encoders**
*   **Concept:** After the initial vector search (retrieval), pass the top-K results through a lightweight cross-encoder model to re-sort them by relevance.
*   **Critique:** Significantly boosts retrieval accuracy, but adds latency.
*   **Feasibility:** Medium. Requires integrating a model like `BGE-Reranker` or similar.
*   **Trade-off:** Latency vs. Precision. Might be overkill for simple queries but essential for complex reasoning.

**Selection:** Option 1 is more foundational for the current RAG architecture. It directly addresses the "Small-to-Big" retrieval pattern identified in my self-correction and aligns with the "Metadata Enrichment" action item.

---

## Idea: Parent-Document Retrieval Integration
Implement a two-tier storage and retrieval strategy where vector search operates on small, semantically dense chunks, while the generation phase retrieves the associated parent document context.

## Why
Current chunking (recursive character) is efficient but often lacks the global context required for high-quality generation. By decoupling the retrieval unit from the generation unit, I can maintain high search precision without sacrificing the context window's coherence.

## Implementation Steps
1.  **Ingestion Update:** Modify the ingestion pipeline to create two levels of chunks: `child_chunks` (e.g., 256 tokens) and `parent_chunks` (e.g., 1024 tokens).
2.  **Metadata Mapping:** Store `parent_id` in the metadata of every `child_chunk`.
3.  **Retrieval Logic:** Update the search function to:
    *   Perform vector search on `child_chunks`.
    *   Extract unique `parent_id`s from the top-K results.
    *   Fetch the full `parent_chunk` content for those IDs.
4.  **Context Assembly:** Pass the retrieved `parent_chunk` content to the LLM instead of the raw `child_chunk`.

## Risk
**Failure Mode:** "Context Bloat." If the retrieval returns too many distinct parent documents, the context window will exceed the model's limit or introduce noise.
**Mitigation:** Implement a strict limit on the number of unique parent documents retrieved (e.g., max 3) and use a simple relevance threshold for the initial vector search.

**Confidence Score:** 8/10

---

### 1% Metric for this cycle:
*   **Metric:** Successful implementation of the parent-document mapping and retrieval logic, verified by a 15% increase in RAG "Hit Rate" on the test suite compared to the baseline fixed-size chunking.