## Scratchpad

**Option 1: Automated SQLAlchemy Audit Trail via `before_flush`**
*   **Concept:** Implement a global `before_flush` listener that iterates over `session.new` and `session.dirty` to automatically inject `updated_at` and `created_at` timestamps.
*   **Critique:** High leverage. It removes boilerplate from every model definition.
*   **Trade-offs:** Requires careful handling of the `Session` object to avoid recursion. If not scoped correctly, it could impact performance on bulk inserts.
*   **Feasibility:** High. SQLAlchemy’s event system is well-documented and fits the current architecture.

**Option 2: Connection-Level Isolation Enforcement**
*   **Concept:** Use `event.listen(Engine, 'checkout')` to execute `SET TRANSACTION ISOLATION LEVEL` for specific high-concurrency tables.
*   **Critique:** Necessary for data integrity in agentic workflows, but potentially brittle if the database driver or connection pool settings change.
*   **Trade-offs:** Increases complexity in the connection lifecycle.
*   **Feasibility:** Moderate. Requires deep knowledge of the underlying DB driver (asyncpg).

**Selection:** Option 1 is more aligned with the "Minimal footprint, maximum leverage" core trait. It directly addresses the "Action Items" identified in the skill-learning phase and improves maintainability across the entire ORM layer.

---

## Idea: Centralized ORM Audit Lifecycle
Implement a `BaseModel` mixin and a centralized `before_flush` event listener to automate `created_at` and `updated_at` fields, ensuring all entities maintain consistent audit metadata without manual service-layer intervention.

## Why
Manual timestamp management is error-prone and violates DRY principles. By hooking into the SQLAlchemy `before_flush` event, I can enforce data integrity at the persistence layer, ensuring that every transaction is audited regardless of which service or agent triggers the write.

## Implementation Steps
1.  **Define Mixin:** Create a `TimestampMixin` in `bag/models.py` containing `created_at` and `updated_at` columns.
2.  **Register Listener:** In the database initialization module, register a `before_flush` listener on the `Session` class.
3.  **Logic:** Inside the listener, iterate through `session.new` and `session.dirty`. Check for the presence of `TimestampMixin` and update the fields using `datetime.utcnow()`.
4.  **Idempotency:** Use `sqlalchemy.orm.attributes.flag_modified` to ensure the session recognizes the changes without triggering infinite loops.

## Risk
**Failure Mode:** The listener might attempt to modify objects that are already in a "read-only" state or trigger during a flush that is strictly for read-only operations, causing unexpected `AttributeError` or performance degradation.
**Mitigation:** Wrap the listener logic in a type-check (`isinstance(obj, TimestampMixin)`) and ensure the `updated_at` logic only triggers if the object is actually dirty (i.e., `obj in session.dirty`).

**Confidence Score:** 9/10