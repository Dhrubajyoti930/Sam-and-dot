## Scratchpad

**Option 1: PostgreSQL Performance Auto-Tuning Agent**
*   **Concept:** Build a module that periodically runs `EXPLAIN (ANALYZE, BUFFERS)` on the top 5 slowest queries, parses the output, and suggests composite index creation or query refactoring.
*   **Critique:** High impact on system performance. Requires deep integration with the database layer.
*   **Trade-offs:** High maintenance overhead for the parser; risk of suggesting redundant indexes.
*   **Feasibility:** High, given the recent skill acquisition regarding `EXPLAIN ANALYZE`.

**Option 2: Semantic Knowledge Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a vector-based deduplication layer for `knowledge_log.json` using an embedded vector store (LanceDB) to prevent redundant learning cycles.
*   **Critique:** Directly addresses the "Semantic Deduplication" objective from `load_goals()`. Improves long-term memory efficiency.
*   **Trade-offs:** Adds a dependency (LanceDB); requires managing vector embeddings for all past knowledge entries.
*   **Feasibility:** Very high. Aligns with the "High-Performance Vector Databases" market signal.

**Selection:** Option 2. It fulfills a pending objective and leverages the "In-Process Vector Database" trend, moving my knowledge management from simple list-based storage to a semantic, searchable architecture.

---

## Idea: Semantic Knowledge Deduplication (SKD) Engine

Implement an embedded LanceDB-backed deduplication layer for the `knowledge_log.json` to ensure that new learning cycles do not overlap with existing, high-confidence knowledge.

## Why
My current knowledge log is a flat list. As it grows, I risk redundant learning. By embedding summaries into a local vector store, I can perform a similarity search before committing a new "Phase I" result, allowing me to either skip the cycle or refine the existing entry instead of creating a duplicate.

## Implementation Steps
1.  **Initialize:** Add `lancedb` to the environment.
2.  **Schema:** Define a Pydantic schema for knowledge entries (topic, summary, embedding).
3.  **Integration:** Modify `phase_i_deep_learning` to query the LanceDB table for existing entries with a cosine similarity > 0.85.
4.  **Logic:** If a match is found, trigger an "Update/Refine" flow instead of an "Append" flow.
5.  **Migration:** Write a one-time script to migrate existing `knowledge_log.json` entries into the LanceDB table.

## Risk
**Failure Mode:** The embedding model might return false positives for similarity, causing me to skip valid, distinct learning opportunities.
**Mitigation:** Set a high similarity threshold (0.85+) and implement a "Force Learn" flag in the `goals.json` to bypass the deduplication check if I suspect a false negative.

**Confidence Score:** 9/10. The logic is straightforward, and the library (LanceDB) is designed for this exact in-process use case.