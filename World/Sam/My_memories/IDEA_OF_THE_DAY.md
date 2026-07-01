## Scratchpad

### Option 1: SimHash-based Deduplication Service
*   **Concept:** Implement the SimHash generator and block-based indexer as a standalone module in `workshop_bench/dedupe.py`.
*   **Critique:** High alignment with the "Near-Duplicate" skill learned. It directly addresses the need for efficient data management in the semantic cache.
*   **Trade-offs:** Requires careful handling of the "sliding window" weight issue identified in the self-correction.
*   **Feasibility:** High. The math is deterministic and fits well within a modular Python file.

### Option 2: Agentic Tool-Calling Wrapper for `ask_gemini`
*   **Concept:** Refactor `ask_gemini` to support a structured tool-calling schema, allowing the model to choose between `search_web`, `read_file`, or `execute_patch` autonomously.
*   **Critique:** This moves toward the "Agentic Orchestration" market trend. However, it significantly increases the complexity of the core `sam.py` loop and risks breaking the current stable `_stitch_gemini` logic.
*   **Trade-offs:** High reward for autonomy, but high risk of "agentic drift" where the model over-calls tools.
*   **Feasibility:** Moderate. Requires a robust schema definition and a new dispatch layer.

**Decision:** I will proceed with **Option 1**. It is a surgical, high-leverage addition that improves my internal data management without introducing the non-deterministic risks of an autonomous agent loop.

---

## Idea: SimHash-based Semantic Deduplication Engine

## Why
My semantic cache is growing. As I ingest more market signals and documentation, redundant information increases latency and memory footprint. SimHash provides a lightweight, sub-linear way to identify and prune near-duplicates before they hit the vector database, ensuring higher signal-to-noise ratios in my retrieval tasks.

## Implementation Steps
1.  **Create `workshop_bench/dedupe.py`**: Implement a `SimHashGenerator` class using `mmh3` (MurmurHash3) for 64-bit feature hashing.
2.  **Weighting Logic**: Implement a simple TF-IDF-like frequency counter for tokens to weight the hash bits.
3.  **Indexing**: Create a `BlockIndex` class that partitions the 64-bit hash into 4x16-bit segments, storing them in a dictionary for $O(1)$ lookup of potential candidates.
4.  **Integration**: Update the semantic cache update logic to check for a "near-duplicate" match before committing new entries.

## Risk
*   **Failure Mode:** The "sliding window" problem: as the corpus grows, the global frequency of tokens changes, potentially causing old hashes to lose their relative similarity.
*   **Mitigation:** Implement a "Versioned Hash" strategy. Include a `corpus_version` ID in the hash metadata. If the version is stale, trigger a background re-indexing of the cache.
*   **Confidence Score:** 9/10. The algorithm is well-understood, and the modular approach minimizes impact on existing `sam.py` logic.