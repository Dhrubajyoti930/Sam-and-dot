## Scratchpad

**Option 1: Recursive Character Text Splitting (RCTS)**
*   **Concept:** Implement a splitter that respects document hierarchy (e.g., `\n\n`, `\n`, ` `) before falling back to sliding window chunking.
*   **Critique:** High alignment with the "Self-Correction" note. It preserves semantic boundaries better than fixed-size sliding windows.
*   **Feasibility:** High. It leverages standard patterns found in libraries like LangChain but can be implemented natively to keep the footprint minimal.
*   **Maintainability:** Excellent. It makes the RAG pipeline more robust to varied document types.

**Option 2: Metadata-Driven "Contextual Breadcrumbs"**
*   **Concept:** Inject a header into every chunk containing the document title, section hierarchy, and a summary of the parent document.
*   **Critique:** Improves retrieval relevance significantly for LLMs, but increases token consumption per query.
*   **Feasibility:** Moderate. Requires a pre-processing pass to generate summaries for each document.
*   **Maintainability:** Good, but adds complexity to the ingestion pipeline.

**Selection:** Option 1 is the logical next step for the RAG architecture. It directly addresses the "hard boundary" problem identified in the self-correction and provides a cleaner foundation for future improvements.

---

## Idea: Recursive Structure-Aware Chunking

Implement a `RecursiveCharacterTextSplitter` utility that prioritizes structural delimiters (`\n\n`, `\n`, `.`, ` `) to ensure chunks align with natural document boundaries, while maintaining a sliding window overlap to preserve context across those boundaries.

## Why
Fixed-size chunking often severs sentences or paragraphs, leading to "context fragmentation." By splitting on structural markers first, we ensure that the retriever captures complete semantic units. The sliding window overlap then acts as a safety net for cross-boundary continuity.

## Implementation Steps
1.  **Define Delimiter Hierarchy:** Create a list of separators in order of preference: `["\n\n", "\n", ". ", " ", ""]`.
2.  **Recursive Logic:** Create a function that attempts to split the text by the first separator. If the resulting chunk is still larger than `chunk_size`, recurse using the next separator in the list.
3.  **Overlap Integration:** Once a chunk is within the `chunk_size` limit, append the specified `overlap` from the end of the previous chunk to the start of the current one.
4.  **Token Validation:** Use `tiktoken` to verify that the final chunk size (including overlap) does not exceed the embedding model's input limit.

## Risk
**Failure Mode:** If a document has no structural delimiters (e.g., a single massive block of text), the recursion will fall back to character-level splitting, which is inefficient.
**Mitigation:** Implement a "hard-stop" character-count fallback that forces a split if a segment remains too large after all delimiters are exhausted.

**Confidence Score:** 9/10

---

## Action Items
```json
[
  {
    "task": "Implement `RecursiveCharacterTextSplitter` in `workshop_bench/chunking.py`.",
    "priority": "high"
  },
  {
    "task": "Update `sam.py` to utilize this new utility for document ingestion.",
    "priority": "medium"
  },
  {
    "task": "Add a unit test in `bag/tests.py` to verify that chunks do not split mid-sentence when `\n` or `. ` delimiters are present.",
    "priority": "medium"
  }
]
```