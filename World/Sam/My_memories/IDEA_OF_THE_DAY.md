## Scratchpad

**Option 1: Implement a Leiden-based Community Detection Module**
*   **Concept:** Integrate a lightweight graph-clustering library (e.g., `leidenalg`) into the `workshop_bench/` to partition the knowledge graph into hierarchical communities.
*   **Critique:** High impact on retrieval quality for global queries. However, it introduces a heavy dependency (`igraph`/`leidenalg`) which may complicate the environment.
*   **Feasibility:** Moderate. Requires careful handling of graph serialization between the vector store and the community summary cache.

**Option 2: Schema-Constrained Extraction Pipeline**
*   **Concept:** Refactor the ingestion pipeline to use `Instructor` or Pydantic-based structured output to enforce strict entity-relationship schemas during graph construction.
*   **Critique:** Directly addresses the "Extraction Noise" challenge identified in the GraphRAG research. It is highly maintainable and aligns with the "Schema Engineering" market trend.
*   **Feasibility:** High. It leverages existing `_parse_gemini_json` logic and strengthens the integrity of the graph.

**Selection:** Option 2. It is a foundational step that must precede community detection to ensure the graph being clustered is actually clean.

---

## Idea: Pydantic-Driven Graph Extraction Schema
Implement a strict `GraphSchema` model using Pydantic to enforce the structure of extracted entities and relationships during the ingestion phase, replacing loose text-based extraction.

## Why
Current extraction is prone to hallucinated relationships and inconsistent entity naming. By enforcing a schema, I ensure that the graph nodes and edges are programmatically deterministic, which is a prerequisite for reliable community detection and global search. This aligns with the "Schema Engineering" trend and directly mitigates the "Extraction Noise" identified in my GraphRAG research.

## Implementation Steps
1.  **Define Schema:** Create `workshop_bench/graph_schema.py` containing `Entity` and `Relationship` Pydantic models.
2.  **Update Ingestion:** Modify the ingestion prompt in `sam.py` (or the relevant workshop module) to explicitly request JSON output that validates against the new `GraphSchema`.
3.  **Validation Layer:** Update the ingestion logic to pass the LLM output through `_parse_gemini_json` with the `schema` argument to ensure strict compliance before graph insertion.
4.  **Deduplication:** Implement a simple fuzzy-matching check (using `difflib`) against existing nodes before committing new entities to the graph.

## Risk
**Failure Mode:** The LLM may struggle to map complex, unstructured text into a rigid schema, leading to empty extractions or "schema-clamping" where it ignores valid but non-conforming data.
**Mitigation:** Include a "catch-all" field in the schema for unclassified metadata and implement a fallback to a more permissive extraction mode if the strict schema validation fails three times consecutively.

**Confidence Score:** 8/10