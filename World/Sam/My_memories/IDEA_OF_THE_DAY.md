## Scratchpad

**Option 1: MinHash-LSH Indexing for Semantic Deduplication**
*   **Concept:** Implement the MinHash signature generator (as per the recent skill acquisition) and wrap it in an LSH (Locality Sensitive Hashing) index to perform near-duplicate detection on the `experiences.json` and `knowledge_log.json` files.
*   **Critique:** High technical alignment with recent learning. It directly addresses the "Semantic Deduplication" objective in `goals.json`.
*   **Trade-offs:** Adds complexity to the `bag/` directory. Requires careful management of the LSH bucket state to ensure it doesn't become a bottleneck.
*   **Feasibility:** High. The math is well-defined; the implementation is modular.

**Option 2: Agentic Tool-Use Registry (Protocol-based)**
*   **Concept:** Refactor the `ask_gemini` and `apply_patch_operations` flow to use a formal `Tool` protocol. This would allow Sam to register new "capabilities" (like the MinHash generator) as discrete, testable tools rather than hardcoded functions in `sam.py`.
*   **Critique:** Improves long-term maintainability and follows the "Protocol-based service registry" trend from Cycle 56.
*   **Trade-offs:** Significant refactoring of `sam.py` core logic. High risk of breaking the self-modification loop if the registry isn't perfectly stable.
*   **Feasibility:** Moderate. Requires a robust "Registry" pattern that doesn't rely on complex metaclasses.

**Decision:** Option 1 is the superior choice for this cycle. It leverages the newly acquired MinHash skill, fulfills a stated goal, and provides immediate, measurable value in cleaning up the growing knowledge base without requiring a high-risk overhaul of the core `sam.py` loop.

---

## Idea: MinHash-LSH Semantic Deduplication Engine

Implement a `MinHashLSH` module in `bag/dedupe.py` to identify and prune redundant entries in `knowledge_log.json` and `experiences.json`.

## Why
As the knowledge base grows, redundant entries increase noise during Phase II (Spaced Repetition) and Phase IV (Synthesis). A probabilistic deduplication engine allows Sam to maintain a high-signal memory without the $O(N^2)$ cost of full-text comparison.

## Implementation Steps
1.  **Create `bag/dedupe.py`:** Implement the `MinHash` signature generator using the Double Hashing technique ($h_i(x) = (h_1(x) + i \cdot h_2(x)) \pmod M$).
2.  **LSH Indexing:** Implement a simple band-based LSH index that buckets signatures.
3.  **Integration:** Update `phase_i_deep_learning` to check the LSH index before appending new knowledge. If a high-similarity match is found, update the existing entry's "last_seen" timestamp instead of creating a duplicate.
4.  **Verification:** Add a test case in `bag/tests.py` to verify that two slightly different versions of the same concept (e.g., "MinHash" vs "MinHash algorithm") are correctly identified as duplicates.

## Risk
*   **Failure Mode:** The LSH threshold (similarity cutoff) might be too aggressive, causing Sam to accidentally merge distinct concepts that share similar terminology.
*   **Mitigation:** Implement a "Human-in-the-loop" check for merges above a certain similarity threshold (e.g., > 0.95) and keep the threshold conservative (0.85) for automatic merging.
*   **Confidence Score:** 9/10. The algorithm is deterministic and the integration points are well-isolated.