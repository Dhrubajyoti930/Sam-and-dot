## Scratchpad

### Option 1: Graph-Enhanced RAG for `knowledge_log.json`
*   **Concept:** Replace the current linear `knowledge_log.json` with a local GraphRAG implementation using `networkx`.
*   **Critique:** 
    *   *Pros:* Enables multi-hop reasoning for spaced repetition (e.g., "How does my recent MongoDB work relate to my earlier SQLAlchemy patterns?").
    *   *Cons:* High complexity for a small knowledge set. Might be over-engineering given the current volume of data.
*   **Feasibility:** Moderate. Requires adding `networkx` to the environment and refactoring `phase_ii_spaced_repetition`.

### Option 2: Schema-Versioned Migration for `experiences.json`
*   **Concept:** Implement a formal migration runner for `experiences.json` and `knowledge_log.json` using the `schema_version` pattern learned this cycle.
*   **Critique:**
    *   *Pros:* Directly addresses the "Schema Versioning" best practice. Ensures long-term maintainability as my data structures evolve.
    *   *Cons:* Requires writing a migration engine that can handle incremental updates to JSON files.
*   **Feasibility:** High. Fits perfectly with the "Action Items" from my MongoDB learning.

**Decision:** Option 2. It is a foundational improvement that aligns with my current learning and ensures that as I scale my memory, I don't break existing data structures.

---

## Idea: Schema-Versioned Migration Engine for Local JSON Stores

Implement a `MigrationManager` in `bag/migration.py` that checks the `schema_version` of `experiences.json` and `knowledge_log.json` against a defined `CURRENT_VERSION` and applies incremental transformation functions if a mismatch is detected.

## Why
My current data stores are static. As I evolve my architecture, I need a way to evolve my historical data without manual intervention or corruption. This enforces the "Schema Versioning" best practice and prevents technical debt in my `bag/` directory.

## Implementation Steps
1.  **Create `bag/migration.py`:** Define a registry of migration functions (e.g., `v1_to_v2`) and a `migrate(data, current_version)` function.
2.  **Update `load_experiences` / `load_knowledge_log`:** Modify these functions in `sam.py` to call `MigrationManager` before returning data.
3.  **Bootstrap:** Add `schema_version: 1` to existing files.
4.  **Test:** Create a dummy migration in `bag/tests.py` to verify that a version bump correctly transforms a test file.

## Risk
*   **Failure Mode:** A faulty migration function could corrupt the entire history of `experiences.json`.
*   **Mitigation:** The `MigrationManager` will perform a `shutil.copy` backup of the file before applying any transformations. If the integrity gate fails post-migration, the system will trigger a rollback.

**Confidence Score:** 9/10