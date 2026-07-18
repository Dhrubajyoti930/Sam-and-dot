## Scratchpad

**Option 1: ColBERT Re-ranking Integration**
*   **Concept:** Integrate a ColBERT re-ranker into the existing RAG pipeline to process the top-k candidates retrieved by the current bi-encoder.
*   **Critique:** High impact on retrieval precision. However, it introduces a significant latency penalty and requires managing a separate index or a heavy inference step.
*   **Feasibility:** Moderate. Requires careful handling of the MaxSim operation and GPU memory constraints.

**Option 2: Semantic Deduplication Pipeline (Refinement)**
*   **Concept:** Build on Cycle 216 by implementing a lightweight, embedding-based deduplication service that runs as a pre-ingestion gate for the RAG system.
*   **Critique:** Directly addresses the "data quality" bottleneck identified in previous cycles. It is lower latency than re-ranking and provides immediate, measurable improvements to index size and retrieval noise.
*   **Feasibility:** High. Leverages existing vector infrastructure.

**Selection:** Option 2. It aligns with my goal of "Minimal footprint, maximum leverage" and directly improves the foundation of the RAG system before adding more complex retrieval layers like ColBERT.

---

## Idea: Embedding-Based Semantic Deduplication Gate

Implement a `DeduplicationGate` in `workshop_bench/` that computes cosine similarity between incoming document chunks and existing index centroids. If a document exceeds a 0.98 similarity threshold, it is flagged as a duplicate and rejected from the ingestion pipeline.

## Why
Standard RAG systems suffer from "context pollution" when redundant information is ingested. By enforcing a semantic uniqueness constraint at the ingestion gate, I reduce index bloat, lower vector search latency, and improve the signal-to-noise ratio for the LLM during retrieval.

## Implementation Steps
1.  **Define Threshold:** Create a configuration constant `SEMANTIC_SIMILARITY_THRESHOLD = 0.98`.
2.  **Gate Logic:** Implement `workshop_bench/deduplication.py` with a `check_uniqueness(embedding, index_centroids)` function.
3.  **Integration:** Update the ingestion script to call `check_uniqueness` before committing new vectors to the database.
4.  **Logging:** Log rejected documents to a `rejected_ingestion.json` file for periodic review.

## Risk
**Failure Mode:** The threshold might be too aggressive, causing the loss of nuanced, slightly overlapping information that is actually distinct (e.g., two versions of a policy document with minor updates).
**Mitigation:** Implement a "soft-reject" mechanism where documents within the 0.95–0.98 range are flagged for manual review rather than discarded, and ensure the threshold is configurable via `bag/config.json`.

**Confidence Score:** 9/10