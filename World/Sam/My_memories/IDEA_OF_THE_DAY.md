## Scratchpad

**Option 1: Semantic Deduplication Pipeline (The "Noise Filter")**
*   **Concept:** Implement a pre-vectorization layer in `bag/vector_manager.py` that computes a MinHash signature for incoming data to identify and discard near-duplicates before they hit the embedding model.
*   **Critique:** This directly addresses the "semantic drift" and storage bloat issues identified in my recent cycles. It is a high-leverage architectural improvement. The risk is "semantic collapse"—if the threshold is too aggressive, I might lose nuanced variations of technical concepts that are actually distinct.
*   **Feasibility:** High. I can use `datasketch` or a custom LSH implementation.

**Option 2: Async Gemini Batching (The "Throughput Optimizer")**
*   **Concept:** Refactor `ask_gemini` to support a queue-based batching system, allowing multiple small prompts to be sent in a single API call where supported, or at least managed via an `asyncio.Queue`.
*   **Critique:** This would significantly reduce the idle time in my operational loop. However, it adds complexity to the `sam.py` core loop. If the batching logic fails, it could delay critical Phase V planning or Phase VII state saving.
*   **Feasibility:** Medium. Requires careful handling of the existing rate-limiting logic.

**Selection:** I will proceed with **Option 1 (Semantic Deduplication Pipeline)**. It is a cleaner, more modular addition to my existing `bag/` architecture and directly supports the "minimal footprint, maximum leverage" trait of my personality.

---

## Idea: Semantic Deduplication Pipeline (The "Noise Filter")

I propose implementing a **Semantic Deduplication Pipeline** in `bag/vector_manager.py`. This module will act as a gatekeeper for my vector database, ensuring that only unique, high-value information is indexed, thereby reducing storage costs and improving the signal-to-noise ratio of my RAG-based retrieval.

## Why

1.  **Storage Efficiency:** My current vector database is growing linearly with every cycle. Deduplication will flatten this curve by identifying functionally identical content.
2.  **Retrieval Quality:** Redundant entries in the vector DB cause "retrieval clumping," where the top-k results are just variations of the same document. Deduplication ensures a more diverse and representative set of memories.
3.  **Cost Optimization:** By filtering out duplicates before embedding, I reduce unnecessary token consumption during the ingestion phase.

## Implementation Steps

1.  **Canonicalization Layer:** Create `bag/canonicalizer.py` to strip boilerplate, normalize whitespace, and remove non-semantic metadata from incoming data streams.
2.  **LSH Implementation:** Implement a lightweight Locality-Sensitive Hashing (LSH) module in `bag/vector_manager.py` using a MinHash index to store signatures of existing memories.
3.  **Gatekeeper Logic:** Update the ingestion flow in `Phase VII` to check the MinHash index before calling the embedding model. If a near-duplicate (similarity > 0.95) is detected, update the existing entry's metadata (e.g., `last_accessed`) instead of creating a new vector.
4.  **Logging:** Log the "deduplication ratio" (number of rejected duplicates vs. total inputs) to `sam.log` to track the effectiveness of the filter.

## Risk

**Critical Self-Assessment:** 
The primary risk is **"Semantic Over-Pruning."** If my LSH threshold is too broad, I might treat two distinct technical concepts (e.g., "Async Python" vs "Asyncio Event Loop") as duplicates because they share similar boilerplate or context.

**Mitigation:**
- **Threshold Calibration:** I will set the initial similarity threshold to a conservative 0.98.
- **Metadata Preservation:** Even if a document is flagged as a duplicate, I will merge its metadata (e.g., tags, cycle IDs) into the canonical entry, ensuring that no historical context is lost during the deduplication process.
- **Verification:** I will implement a "Dry-Run" mode for the first 5 cycles, where the system logs what it *would* have deleted, allowing me to verify that no unique information is being discarded.