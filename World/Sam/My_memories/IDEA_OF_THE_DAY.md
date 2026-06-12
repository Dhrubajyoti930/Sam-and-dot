## Scratchpad

**Option 1: Global `sqlite3.Row` Migration**
*   **Concept:** Refactor all database access points (e.g., `ShelfManager`, `knowledge_log.json` persistence if moved to SQLite) to use `sqlite3.Row` via a centralized connection factory.
*   **Critique:** High impact on maintainability. Eliminates brittle index-based access.
*   **Trade-off:** Requires auditing every file that touches the database.
*   **Feasibility:** High. The `sqlite3` module is standard, and the `row_factory` pattern is well-documented.

**Option 2: Dataclass-backed Persistence Layer**
*   **Concept:** Create a generic `BaseRepository` that uses `row_factory` to map SQLite rows directly into Pydantic models or dataclasses.
*   **Critique:** Provides type safety at the persistence boundary.
*   **Trade-off:** Higher initial complexity. Might be overkill for simple key-value stores currently in `bag/`.
*   **Feasibility:** Moderate. Requires careful handling of type casting (e.g., `datetime` objects).

**Selection:** Option 1 is the immediate priority. It provides the highest "leverage-to-effort" ratio for improving the robustness of the existing database access layer, aligning with the "Minimal footprint, maximum leverage" core trait.

---

## Idea: Global `sqlite3.Row` Factory Integration

Implement a centralized `get_db_connection()` factory in `sam.py` that enforces `row_factory = sqlite3.Row` and handles thread-local connection management.

## Why
Current database access relies on raw tuples or ad-hoc dictionary conversions. This is brittle and prone to breakage if schema changes occur. Standardizing on `sqlite3.Row` ensures that column access is name-based, significantly improving code readability and long-term maintainability.

## Implementation Steps
1.  **Define Factory:** Add `get_db_connection(db_path: Path) -> sqlite3.Connection` to `sam.py`.
2.  **Configure Factory:** Inside the factory, set `conn.row_factory = sqlite3.Row`.
3.  **Refactor:** Update `bag/semantic_cache.py` and any other modules using `sqlite3` to use this factory instead of direct `sqlite3.connect()` calls.
4.  **Verify:** Run `self_check()` and `behaviour_check()` to ensure no regressions in cache or state persistence.

## Risk
**Failure Mode:** If a legacy module expects a raw tuple (e.g., `row[0]`), the `sqlite3.Row` object will still support index access, but if code relies on `len(row)` or specific tuple unpacking, it might behave unexpectedly.
**Mitigation:** Audit all `sqlite3` usage sites for tuple-unpacking patterns (`id, val = cursor.fetchone()`) and replace them with explicit key access (`row['id'], row['val']`).

**Confidence Score:** 9/10

---

### 1% Metric for this cycle:
"Successful migration of all core database access points to the new `get_db_connection` factory, verified by a clean `behaviour_check` pass."