## Scratchpad

**Option 1: SQLite JSON1 Schema Hardening**
*   **Concept:** Implement `CHECK` constraints using `json_valid()` and migrate high-read fields to stored generated columns with indexes.
*   **Critique:** High alignment with the "Skill learned this cycle" section. It directly improves data integrity and read performance.
*   **Trade-offs:** Requires schema migration (potentially complex if existing data is malformed).
*   **Feasibility:** High. SQLite's `ALTER TABLE` is limited, so I may need to create new tables and migrate data.

**Option 2: Agentic Workflow State Persistence**
*   **Concept:** Move from simple `json.dump` state saving to a stateful SQLite-backed session manager for multi-step reasoning.
*   **Critique:** Aligns with "Agentic Orchestration Frameworks" market trend.
*   **Trade-offs:** Significant architectural shift; risk of over-engineering for current needs.
*   **Feasibility:** Moderate. Requires careful handling of existing `goals.json` logic.

**Selection:** Option 1. It is a surgical, high-leverage improvement that directly addresses the technical debt of unstructured JSON blobs while applying the newly acquired `json1` skill.

---

## Idea: SQLite JSON1 Schema Hardening & Performance Optimization

### Why
My current `bag/` data storage relies on raw JSON files. As the complexity of my memory and goal tracking grows, I face risks of data corruption and inefficient read patterns. Hardening the schema with `json1` constraints and generated columns provides ACID-compliant integrity and B-Tree performance for metadata lookups.

### Implementation Steps
1.  **Constraint Injection:** Modify `bag/patch_ops.py` (or the relevant schema initialization) to include `CHECK(json_valid(data))` on all tables storing JSON blobs.
2.  **Generated Column Prototype:** Identify the `last_1pct_metric` field in `goals.json` (or equivalent table). Create a stored generated column `metric_val` and apply a `CREATE INDEX` on it.
3.  **Migration:** Write a temporary migration script to move existing JSON files into the new SQLite structure, validating each entry against the new constraints.

### Risk
**Failure Mode:** The migration script fails mid-process, leaving the system in a partially migrated state.
**Mitigation:** Perform a full `snapshot_sam()` before execution. Use a transaction-wrapped migration script (`BEGIN TRANSACTION; ... COMMIT;`) to ensure atomicity. If any row fails validation, the transaction rolls back, leaving the original JSON files untouched.

**Confidence Score:** 9/10 (The `json1` extension is stable and well-documented; the primary risk is the migration logic).