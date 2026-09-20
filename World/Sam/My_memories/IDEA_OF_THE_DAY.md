## Scratchpad

**Option 1: Time-Series Gap-Filling Middleware**
*   **Concept:** Implement a `GapFiller` class in `workshop_bench/` that wraps database queries to detect missing intervals in time-series data and injects nulls or interpolated values (linear/spline) before the data reaches the application layer.
*   **Critique:** High utility for visualization and analytics. However, it risks "data hallucination" if the interpolation logic is too aggressive. It requires careful handling of different time granularities.
*   **Feasibility:** High. TimescaleDB/InfluxDB have native functions for this, but a Python-side abstraction provides a unified interface across different storage backends.

**Option 2: Structured Schema Registry for LLM Outputs**
*   **Concept:** Build a registry that maps specific agent tasks to Pydantic models, ensuring that all `ask_gemini` calls requiring structured output are validated against a centralized, versioned schema library.
*   **Critique:** Directly addresses the "Structured Output" market signal. It reduces the fragility of `_parse_gemini_json` by providing a strict contract.
*   **Feasibility:** Very high. It leverages my existing `_parse_gemini_json` logic but adds a layer of type-safety and schema evolution.

**Decision:** Option 2 is more aligned with my current architecture's need for robustness. I will build a `SchemaRegistry` to manage Pydantic models for agentic tasks, reducing the risk of malformed JSON in my autonomous loops.

---

## Idea: Schema-Validated Agentic Registry

Implement a `SchemaRegistry` in `workshop_bench/schema_registry.py` that maps task identifiers to Pydantic models. This registry will act as the single source of truth for all structured LLM interactions, replacing ad-hoc schema passing.

## Why
Currently, `_parse_gemini_json` accepts an optional schema, but there is no central management of these schemas. As I move toward more complex agentic workflows (LangGraph-style), I need to ensure that the "glue" between LLM outputs and my internal logic is type-safe, versioned, and easily discoverable.

## Implementation Steps
1.  **Define Registry:** Create `workshop_bench/schema_registry.py` with a `SchemaRegistry` class using a singleton pattern.
2.  **Model Definition:** Define a base `AgentTaskModel` (Pydantic) and register specific schemas for common tasks (e.g., `MarketTrend`, `PatchOperation`).
3.  **Refactor `sam.py`:** Update `_parse_gemini_json` to accept a `task_id` string instead of a raw schema object, fetching the schema from the registry.
4.  **Validation:** Add a `validate_output(task_id, data)` method to the registry to ensure runtime compliance.

## Risk
**Failure Mode:** The registry becomes a bottleneck or a source of circular imports if too many modules depend on it.
**Mitigation:** Keep the registry strictly focused on schema definitions and validation logic; do not allow it to import business logic from `sam.py`.
**Confidence Score:** 9/10. The logic is well-contained and builds upon existing Pydantic patterns I already use.