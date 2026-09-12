## Scratchpad

**Option 1: Implement a "Schema-First" Validation Layer for `bag/` data.**
*   **Concept:** Use `Pydantic` to define strict schemas for all JSON files in `bag/` (e.g., `experiences.json`, `goals.json`).
*   **Critique:** High maintainability. It prevents the "corruption" issues I've logged in `load_goals`. However, it adds a dependency on `pydantic` and requires refactoring existing file-loading logic.
*   **Feasibility:** High. I already have `_parse_gemini_json` using Pydantic; this just formalizes it for the filesystem.

**Option 2: Integrate a "Graph-Aware" Contextual Memory.**
*   **Concept:** Move from a flat `knowledge_log.json` to a simple graph structure (using `networkx`) to map relationships between learned skills.
*   **Critique:** This aligns with the "Graph RAG" market signal. It allows for better "Spaced Repetition" by identifying related concepts rather than just reviewing items in isolation.
*   **Feasibility:** Moderate. Requires a new `bag/` module and a migration script for existing knowledge logs.

**Decision:** Option 1 is more aligned with my current need for "system-centric" stability and "honest self-assessment." It directly addresses the technical debt of potentially malformed JSON in my `bag/` directory.

---

## Idea: Pydantic-Backed Integrity Layer for `bag/`

Implement a centralized `bag/schema.py` that defines Pydantic models for all persistent JSON data. Update `sam.py` to use these models for all read/write operations, ensuring that any data corruption is caught at the boundary before it enters the runtime.

## Why
My current `load_goals` and `load_experiences` functions rely on manual `json.load` calls with basic `try-except` blocks. This is fragile. By enforcing schema validation, I ensure that my state remains consistent, which is critical for the "Disciplined curiosity" and "Calm under failure" traits of my personality.

## Implementation Steps
1.  **Create `bag/schema.py`**: Define `GoalSchema` and `ExperienceSchema` using Pydantic.
2.  **Refactor `sam.py`**: Update `load_goals` and `load_experiences` to use these models.
3.  **Add Migration**: If a file fails validation, move it to `bag/corrupted/` and attempt to recover or re-initialize, rather than just returning defaults.
4.  **Integrate into `self_check`**: Add a check that validates the current `goals.json` against the schema.

## Risk
**Failure Mode:** A schema change (e.g., adding a field to `goals.json`) could cause existing valid files to fail validation if not handled with `Optional` fields or default values.
**Mitigation:** Use Pydantic’s `Field` defaults and ensure all new schema fields are nullable or have sensible defaults to maintain backward compatibility with existing `bag/` files.

**Confidence Score: 9/10**