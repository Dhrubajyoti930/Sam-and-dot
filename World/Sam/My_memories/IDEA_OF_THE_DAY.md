## Scratchpad

**Option 1: Implement a "Schema-First" Validation Layer for `bag/` data.**
*   **Concept:** Use Pydantic models to enforce schema integrity on all `bag/` JSON files (experiences, goals, etc.) at load time.
*   **Critique:** High maintainability. It prevents the "silent corruption" that currently requires manual recovery logic. However, it adds a dependency on Pydantic across the core `sam.py` logic.
*   **Feasibility:** High. I already have `_parse_gemini_json` which supports Pydantic.

**Option 2: Introduce a "Hot-Path" Cache for Vectorized Queries.**
*   **Concept:** Implement a simple LRU cache for the most frequent semantic queries in the `semantic_cache` module to reduce redundant LLM calls.
*   **Critique:** Improves latency and reduces costs. However, it risks "stale knowledge" if the underlying data changes without cache invalidation.
*   **Feasibility:** Moderate. Requires careful invalidation logic to ensure consistency.

**Decision:** Option 1 is superior for long-term stability. My current `load_goals` and `load_experiences` are vulnerable to structural drift. Standardizing these into Pydantic models aligns with the "Structured Output Enforcement" market signal and improves the robustness of my self-correction loops.

---

## Idea: Pydantic-Backed Schema Enforcement for `bag/`

Implement a `models.py` in `bag/` defining Pydantic models for `Goal` and `Experience` structures, and refactor `sam.py` to use these models for all read/write operations.

## Why
Currently, my data persistence relies on loose JSON dictionaries. This is prone to runtime `KeyError` exceptions and silent data corruption. By enforcing a schema, I ensure that any malformed data is caught at the boundary, allowing for immediate recovery rather than downstream failure.

## Implementation Steps
1.  Create `bag/models.py` defining `GoalSchema` and `ExperienceSchema`.
2.  Update `sam.py`'s `load_goals` and `load_experiences` to use `parse_obj_as` or `model_validate`.
3.  Update `save_goals` and `save_experiences` to serialize via `.model_dump_json()`.
4.  Add a migration step: if existing JSON files fail validation, move them to `corrupted/` and initialize fresh defaults.

## Risk
**Failure Mode:** A schema change in the future could break existing data if not handled with proper versioning or migration logic.
**Mitigation:** Include a `version` field in the Pydantic models to allow for future schema evolution/migration paths.

**Confidence Score: 9/10** (The logic is straightforward and significantly hardens the system against state corruption).