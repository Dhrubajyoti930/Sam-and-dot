## Scratchpad

### Option 1: Embedding-Aware Parent Summarization
*   **Concept:** Instead of just storing parent chunks, generate a dense summary vector for each parent node. Use this for the initial retrieval pass to ensure the "global" topic matches the query before drilling down into child chunks.
*   **Critique:** High retrieval precision. However, it introduces a significant compute overhead during indexing (LLM calls for every parent summary) and increases the complexity of the vector database schema.
*   **Feasibility:** High, but requires careful management of the embedding model's context window.

### Option 2: Metadata-Driven Context Injection
*   **Concept:** Enhance the hierarchical chunking by injecting a "breadcrumb" string into the metadata of every child chunk (e.g., `path: "Docs > Section 1 > Subsection 1.2"`).
*   **Critique:** Extremely low overhead. It provides the LLM with immediate structural awareness without needing to retrieve the entire parent document. It is highly maintainable and fits perfectly into the existing `sam.py` architecture.
*   **Feasibility:** Very high. This is a surgical improvement to the current chunking logic.

**Decision:** Option 2 is the superior choice for this cycle. It aligns with the "minimal footprint, maximum leverage" trait and directly addresses the "lost in the middle" phenomenon mentioned in my skill learning.

---

## Idea: Structural Breadcrumb Injection for RAG Retrieval

Implement a metadata-enrichment layer in the document parser that maps the header hierarchy to a "breadcrumb" string, which is then injected into the metadata of every child chunk during the indexing phase.

## Why
Current hierarchical chunking provides parent-child relationships, but child chunks often lose their semantic "place" when retrieved in isolation. By embedding the path (e.g., `Root > Chapter > Section`) directly into the chunk metadata, the LLM receives immediate context about the chunk's scope without requiring the retrieval of the entire parent document, reducing token usage and improving reasoning accuracy.

## Implementation Steps
1.  **Modify Parser:** Update the recursive Markdown parser to maintain a `current_path` stack while traversing the document tree.
2.  **Metadata Update:** Append the `current_path` string to the metadata dictionary of each chunk node.
3.  **Retrieval Logic:** Update the retrieval function to include the `breadcrumb` field in the context provided to the LLM.
4.  **Verification:** Run a test case where a query is ambiguous without the breadcrumb but clear with it.

## Risk
**Failure Mode:** The breadcrumb string could become too long for documents with deep nesting, potentially consuming excessive tokens or confusing the embedding model if the metadata is included in the vectorization process.
**Mitigation:** Truncate breadcrumbs to the last three levels of the hierarchy and ensure metadata is excluded from the embedding vector (used only for LLM context).

**Confidence Score:** 9/10