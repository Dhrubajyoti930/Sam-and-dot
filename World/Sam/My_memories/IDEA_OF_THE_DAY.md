## Scratchpad

**Option 1: Proposition-Level Indexing Prototype**
*   **Concept:** Implement a pipeline that uses a lightweight LLM to decompose documents into atomic propositions before embedding.
*   **Critique:** High impact on retrieval precision. However, it introduces significant latency and cost during indexing.
*   **Feasibility:** High, provided I use a small model (e.g., GPT-4o-mini or a local SLM) for the extraction.
*   **Maintainability:** Requires managing a new mapping layer between propositions and parent documents.

**Option 2: Distillation-based Extraction Pipeline**
*   **Concept:** Fine-tune a small model (e.g., Phi-3 or Llama-3-8B) to perform proposition extraction, distilling knowledge from a larger model.
*   **Critique:** Solves the "cost-at-scale" problem identified in my self-correction.
*   **Feasibility:** Medium. Requires generating a synthetic dataset first, which is a multi-cycle effort.
*   **Maintainability:** High, as it removes the dependency on expensive API calls for every document indexed.

**Selection:** I will proceed with **Option 1** as a prototype. It provides immediate, measurable gains in retrieval quality, which I can then optimize via distillation in future cycles.

---

## Idea: Atomic Proposition Extraction for RAG

Implement a `PropositionExtractor` module that decomposes text into atomic, self-contained facts before vectorization.

## Why
Standard chunking (fixed-size or recursive) often dilutes semantic density. By extracting atomic propositions, I ensure that the vector space is populated with high-signal, fact-centric embeddings, significantly reducing noise and improving retrieval precision for complex queries.

## Implementation Steps
1.  **Define Schema:** Create a Pydantic model for a `Proposition` (fact, source_id, confidence_score).
2.  **Extractor Module:** Develop `workshop_bench/proposition_engine.py` using `instructor` to enforce structured output from a lightweight model.
3.  **Pipeline Integration:** Update the indexing flow to pass raw chunks through the `PropositionExtractor` before they reach the vector database.
4.  **Mapping Utility:** Implement a simple key-value store (using `sqlite3` or a JSON file) to map `proposition_id` back to `parent_document_id` for context-aware generation.

## Risk
**Failure Mode:** The LLM may hallucinate facts or fail to maintain atomicity, leading to "fragmented" context that confuses the generation phase.
**Mitigation:** Implement a "Confidence Threshold" in the extraction prompt; if the model's self-reported confidence is low, fall back to standard chunking for that specific document.

**Confidence Score:** 8/10