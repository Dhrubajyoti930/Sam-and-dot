## Scratchpad

### Option 1: Reactive Stream Parser for API Client
*   **Concept:** Implement a `ReadableStream` wrapper in `sam.py` to handle partial JSON chunks from the Gemini API, specifically targeting the `_stitch_gemini` logic.
*   **Critique:** 
    *   *Pros:* Directly addresses the "streaming" skill learned this cycle; improves robustness against network-induced truncation.
    *   *Cons:* Increases complexity of `_stitch_gemini`. Requires careful state management to ensure the parser doesn't "hang" if a chunk is malformed.
    *   *Feasibility:* High. The logic is well-defined in the "Technical Summary."

### Option 2: Hybrid RAG Indexing for `bag/`
*   **Concept:** Integrate BM25 keyword search alongside existing vector embeddings for the `knowledge_log.json` and `experiences.json` files.
*   **Critique:**
    *   *Pros:* Directly addresses the "High-Performance Vector Search" market signal. Improves retrieval accuracy for specific technical terms.
    *   *Cons:* Requires adding a dependency or a lightweight BM25 implementation. Might be overkill for the current size of `bag/`.
    *   *Feasibility:* Moderate.

**Decision:** Option 1 is more aligned with my current architecture and the "Streaming" skill acquisition. It directly improves the reliability of my core communication loop.

---

## Idea: Reactive JSON Stream Buffer
Implement a stateful `JSONStreamBuffer` class in `sam.py` that accumulates partial chunks and validates JSON completeness using a stack-based counter (tracking `{}` and `[]` depth) before attempting a full parse.

## Why
My current `_is_truncated` logic is heuristic and prone to false positives/negatives. A stateful buffer that tracks bracket depth provides deterministic detection of "complete" JSON objects, allowing me to process streams as they arrive rather than relying on post-hoc stitching.

## Implementation Steps
1.  **Define `JSONStreamBuffer`:** Create a class that maintains an internal string buffer and a `depth` counter.
2.  **Integrate with `_stitch_gemini`:** Replace the heuristic `_is_truncated` with a call to `buffer.is_complete()`.
3.  **Refactor `_parse_gemini_json`:** Update to accept the buffered stream, ensuring it only attempts parsing when the depth is zero.
4.  **Test:** Create a test case in `bag/tests.py` that feeds a JSON object in 1-character increments to verify the buffer correctly identifies the completion point.

## Risk
*   **Failure Mode:** The buffer might get stuck in a "non-zero depth" state if the LLM sends malformed JSON that never closes a bracket, leading to a "zombie" stream that never triggers a parse.
*   **Mitigation:** Implement a `max_buffer_size` and a `timeout` mechanism. If the buffer exceeds 16KB or remains open for >10 seconds, force-flush and log a "Malformed Stream" error.
*   **Confidence Score:** 9/10. The logic is deterministic and fits well within the existing `sam.py` structure.