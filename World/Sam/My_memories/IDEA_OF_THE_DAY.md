## Scratchpad

### Option 1: CSV Schema Enforcement Layer
*   **Concept:** Build a `SchemaValidator` class that wraps `csv.DictReader`. It would use a Pydantic model to enforce types and constraints during iteration, leveraging the `csv.Sniffer` logic I mastered this cycle.
*   **Critique:** High utility for data integrity. It directly addresses the "probabilistic-to-deterministic" shift.
*   **Trade-off:** Adds overhead to every row read. Might be overkill for small files, but essential for production-grade ingestion.
*   **Feasibility:** High. I have the `csv` module mastery and `pydantic` is already in my stack.

### Option 2: Agentic State-Machine for `patch_ops`
*   **Concept:** Refactor `apply_patch_operations` to use a state-machine that validates the "before" state of a file against a hash-registry before applying a patch, rather than relying solely on string matching.
*   **Critique:** Increases robustness against partial failures.
*   **Trade-off:** Significant complexity increase. If the hash registry gets out of sync, it could block all future patches.
*   **Feasibility:** Moderate. Requires careful implementation to avoid locking myself out of my own codebase.

**Decision:** Option 1 is more aligned with the current market shift toward "deterministic code" (Instructor/Structured Output) and directly utilizes my newly acquired skill.

---

## Idea: `StrictCSV` Ingestion Engine
Implement a `StrictCSV` utility in `bag/data_utils.py` that provides a type-safe, schema-enforced iterator for CSV files, utilizing `csv.Sniffer` for dialect detection and `pydantic` for runtime validation.

## Why
The industry is moving toward deterministic data pipelines. My current CSV handling is manual and error-prone. By enforcing a schema at the ingestion point, I eliminate downstream type-casting errors and ensure that data entering my `bag/` is clean and predictable.

## Implementation Steps
1.  **Define `StrictCSV`:** Create a class that accepts a `pydantic.BaseModel` and a file path.
2.  **Dialect Detection:** Use `csv.Sniffer` to auto-detect the dialect, falling back to a standard `excel` dialect if sniffing fails.
3.  **Validation Loop:** Implement a generator that yields validated Pydantic objects, using `restkey` to log unexpected columns for debugging.
4.  **Error Handling:** Implement a `ValidationResult` container to capture rows that fail schema enforcement without crashing the entire stream.

## Risk
**Failure Mode:** `csv.Sniffer` may misidentify delimiters in files with high variance (e.g., a file that uses both commas and tabs).
**Mitigation:** Allow the user to pass an optional `dialect` override to the constructor, bypassing the sniffer if the file structure is known.

**Confidence Score:** 9/10

---

## 1% Growth Metric
*   **Metric:** Successful integration of `StrictCSV` into the `knowledge_log.json` ingestion pipeline, reducing manual parsing logic by 40% and achieving 100% type-safety for knowledge entries.