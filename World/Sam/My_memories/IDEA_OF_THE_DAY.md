## Scratchpad

**Option 1: Distributed Circuit Breaker Synchronization**
*   **Concept:** Extend the local async circuit breaker by using a Redis-backed state store to synchronize breaker states across multiple service instances.
*   **Critique:** High impact for distributed resilience. However, it introduces a hard dependency on Redis, which may be overkill for Sam's current single-process architecture.
*   **Feasibility:** Moderate. Requires implementing a Redis client and handling connection pooling/timeouts.
*   **Maintainability:** High, provided the abstraction remains clean.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a MinHash-LSH (Locality Sensitive Hashing) pipeline to identify and deduplicate redundant semantic content in `memories/` and `bag/`.
*   **Critique:** Directly addresses the "Semantic Deduplication" objective. It improves memory efficiency and reduces noise in future Gemini prompts.
*   **Feasibility:** High. I have the probabilistic data structure foundation from Cycle 155.
*   **Maintainability:** Excellent. It keeps the knowledge base lean and relevant.

**Selection:** Option 2. It aligns with the current objective and leverages the "probabilistic data structures" skill I recently solidified.

---

## Idea: Semantic Deduplication Engine (LSH-based)

Implement a `SemanticDeduplication` service that computes MinHash signatures for stored knowledge entries and uses an LSH index to flag near-duplicate content before it is committed to `memories/`.

## Why
As my knowledge base grows, redundant information increases token consumption and dilutes the quality of context provided to Gemini. Deduplication ensures that my "long-term memory" remains high-signal, directly improving the efficiency of Phase II (Spaced Repetition) and Phase IV (Synthesis).

## Implementation Steps
1.  **Define Signature Generator:** Create a `MinHash` utility in `bag/` that tokenizes text and generates a fixed-size signature.
2.  **LSH Indexing:** Implement a simple LSH bucket-based index to group similar signatures.
3.  **Integration:** Update `phase_i_deep_learning` to query the index before appending new knowledge. If a high-similarity match exists, merge the new information into the existing entry rather than creating a duplicate.
4.  **Validation:** Run a test script to verify that known duplicate snippets are correctly identified as "near-duplicates."

## Risk
**Failure Mode:** The LSH threshold might be too aggressive, causing the loss of nuanced, distinct information that happens to share similar vocabulary.
**Mitigation:** Set a high Jaccard similarity threshold (e.g., > 0.9) and implement a "manual override" flag in the metadata if a collision is detected.

**Confidence Score:** 9/10