## Scratchpad

**Option 1: Schema Registry for Event Producers**
*   **Concept:** Implement a local `SchemaRegistry` class in `bag/` that validates all outgoing event payloads against Pydantic models before they hit the log.
*   **Critique:** High long-term value for data integrity. However, it adds complexity to the `patch_ops` workflow. If the schema registry itself is buggy, it blocks all system progress.
*   **Feasibility:** High. I already use Pydantic for `_parse_gemini_json`.

**Option 2: State-Backend Performance Profiling (Flink-lite)**
*   **Concept:** Introduce a `StateStore` interface in `bag/` that abstracts local storage (RocksDB vs. JSON-file-backed) to prepare for high-cardinality windowing.
*   **Critique:** This is a significant architectural shift. It might be premature given my current scale. It risks "over-engineering" before the data volume justifies it.
*   **Feasibility:** Moderate. Requires careful handling of file locks and concurrency.

**Decision:** I will pursue **Option 1**. It aligns with the "Structured Output Enforcement" market signal and directly addresses the "Schema Evolution" requirement of the Kappa architecture I learned this cycle. It is a surgical, high-leverage improvement.

---

## Idea: Pydantic-Backed Schema Registry for Event Integrity

## Why
As I move toward a Kappa-style architecture, the "Immutable Log" is my source of truth. If I write malformed JSON to my logs, reprocessing becomes a nightmare. A central `SchemaRegistry` ensures that any event produced by my internal agents is type-safe and schema-compliant before it is persisted.

## Implementation Steps
1.  **Define `bag/schema_registry.py`**: Create a registry that maps event types (e.g., `cycle_start`, `patch_applied`) to specific Pydantic models.
2.  **Integrate into `sam.py`**: Update `_parse_gemini_json` to optionally use the registry for validation.
3.  **Add Validation Gate**: Wrap the event-writing logic in `sam.py` to pass data through the registry before disk I/O.
4.  **Test**: Add a test case in `bag/tests.py` that attempts to write an invalid event and verifies that the registry raises a `ValidationError`.

## Risk
**Failure Mode:** The registry becomes a bottleneck or a single point of failure if a schema update is incompatible with existing historical logs.
**Mitigation:** Implement "Schema Versioning" in the registry. Each event must include a `version` field, and the registry will support multiple versions of a model simultaneously to ensure backward compatibility during log replay.

**Confidence Score:** 9/10