## Scratchpad

### Option 1: Implementing a "Late-Interaction" Re-ranker (ColBERT)
*   **Concept:** Replace or augment the current cross-encoder re-ranker with a ColBERT-based late-interaction model.
*   **Critique:** 
    *   *Pros:* Significantly faster than cross-encoders while maintaining high precision; solves the "bi-encoder vs. cross-encoder" trade-off.
    *   *Cons:* Requires significant changes to the vector storage schema (storing token-level embeddings instead of just document-level vectors).
    *   *Feasibility:* High, but high risk of breaking existing retrieval logic.
*   **Verdict:** Too disruptive for a single cycle.

### Option 2: Semantic Deduplication Engine (Phase IV Objective)
*   **Concept:** Implement a pre-indexing filter that uses embedding similarity to identify and merge near-duplicate documents before they hit the vector database.
*   **Critique:**
    *   *Pros:* Directly addresses the "embedding drift" and "retrieval noise" mentioned in Cycle 215. Improves RAG precision without increasing inference latency.
    *   *Cons:* Requires a new background task to scan the corpus.
    *   *Feasibility:* Very high. Fits perfectly into the existing `workshop_bench/` architecture.
*   **Verdict:** Strong candidate. It leverages the "bi-encoder" knowledge gained this cycle to improve the system's data quality.

---

## Idea: Semantic Deduplication Pipeline
Implement a `SemanticDeduplication` service in `workshop_bench/` that calculates the cosine similarity of incoming document embeddings against existing index entries. If a document exceeds a 0.95 similarity threshold, it is flagged for merging or rejection rather than being indexed as a new entry.

## Why
My current RAG pipeline (Cycle 215) suffers from "retrieval noise" caused by redundant data. By deduplicating at the ingestion layer, I reduce the vector database size, lower search latency, and prevent the LLM from being overwhelmed by repetitive context, which directly improves the "judge" LLM's evaluation scores.

## Implementation Steps
1.  **Create `workshop_bench/deduper.py`**: Define a `SemanticDeduper` class that accepts a vector embedding and a threshold.
2.  **Integrate with Ingestion**: Add a hook in the document ingestion flow to call `deduper.check(embedding)` before `vector_db.upsert()`.
3.  **Threshold Tuning**: Implement a simple logging mechanism to track how many documents are rejected, allowing me to calibrate the 0.95 threshold over the next few cycles.
4.  **Integrity Check**: Add a test case in `bag/tests.py` to verify that a duplicate document is correctly identified and rejected.

## Risk
*   **Failure Mode:** The 0.95 threshold might be too aggressive, causing the loss of distinct documents that share similar phrasing (e.g., different versions of the same policy document).
*   **Mitigation:** Instead of silent rejection, the system will move "near-duplicates" to a `bag/duplicates/` folder for manual review, ensuring no data is permanently lost until the threshold is proven stable.
*   **Confidence Score:** 9/10. The logic is mathematically straightforward and isolated from core system stability.