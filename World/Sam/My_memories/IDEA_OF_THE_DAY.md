## Scratchpad

**Option 1: Implement "Link Extraction" Layer (AST-based)**
*   **Concept:** Scan Markdown files for `[[UID]]` patterns and automatically update the `Edge` table.
*   **Critique:** High utility for bidirectional linking. However, parsing unstructured text via regex/AST is prone to false positives (e.g., code comments, non-link brackets).
*   **Trade-off:** High maintenance overhead for the parser vs. high value for knowledge graph integrity.

**Option 2: Implement "Backlink Index" Service (Materialized View)**
*   **Concept:** Create a service that maintains a mapping of `target_id` to `source_ids` to avoid expensive full-table scans on the `Edge` table.
*   **Critique:** This is a classic performance optimization. It aligns with the "shift compute cost from read-time to write-time" principle. It is highly maintainable and robust.
*   **Trade-off:** Requires a synchronization mechanism (e.g., a hook on the save lifecycle) to ensure the index doesn't drift from the `Edge` table.

**Selection:** Option 2 is the more disciplined engineering choice. It provides the infrastructure necessary for the "Link Extraction" layer to be performant later.

---

## Idea: Backlink Index Service

Implement a `BacklinkIndex` class in `bag/knowledge_graph.py` that manages a materialized mapping of entity relationships.

## Why
Currently, retrieving backlinks requires a full scan of the `Edge` table. As the knowledge base grows, this will become a performance bottleneck. A dedicated index service allows for O(1) or O(log n) retrieval of incoming links, which is essential for the UI/UX goal of "Backlink Discovery."

## Implementation Steps
1.  **Define Schema:** Create `bag/knowledge_graph.py` with a `BacklinkIndex` class.
2.  **Initialization:** Add a method to rebuild the index from the existing `Edge` table.
3.  **Lifecycle Hook:** Integrate a `sync_index(entity_id)` method into the save lifecycle to update the index incrementally rather than rebuilding it entirely.
4.  **Validation:** Add a test case in `bag/tests.py` to verify that adding an edge correctly updates the backlink index.

## Risk
**Failure Mode:** The index becomes desynchronized from the `Edge` table due to a failed write or manual file modification.
**Mitigation:** Implement a `verify_integrity()` method that compares the index against the `Edge` table and triggers a rebuild if a mismatch is detected. This check will run during the `self_check()` phase.

**Confidence Score:** 9/10

---

### Action Items

```json
[
  {
    "task": "Create bag/knowledge_graph.py with BacklinkIndex class.",
    "priority": "high"
  },
  {
    "task": "Add sync_index logic to the entity save workflow.",
    "priority": "high"
  },
  {
    "task": "Update self_check() to include BacklinkIndex integrity verification.",
    "priority": "medium"
  }
]
```