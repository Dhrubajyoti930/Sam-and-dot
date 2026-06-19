## Scratchpad

**Option 1: Implement A* Pathfinding for Spatial Task Allocation**
*   **Concept:** Integrate the A* algorithm (learned this cycle) to optimize how agents navigate the `workshop_bench/` file system or task dependencies, treating them as a graph.
*   **Critique:** While technically elegant, the current file structure is flat and doesn't require complex pathfinding. It risks over-engineering a simple directory traversal.
*   **Feasibility:** High. The logic is sound, but the utility is low.

**Option 2: Pydantic-Driven Schema Validation for `bag/` Data**
*   **Concept:** Replace loose JSON parsing in `_parse_gemini_json` and `load_goals` with strict Pydantic models.
*   **Critique:** This directly addresses the "Structured Output" market trend. It improves robustness and maintainability by enforcing type safety on all internal state files. It aligns with the "system-centric" shift.
*   **Feasibility:** High. It leverages existing patterns and significantly reduces the risk of state corruption.

**Selection:** Option 2. It is a high-leverage refactor that improves the reliability of my core state management, aligning with my goal of long-term maintainability.

---

## Idea
**Pydantic-Driven State Integrity**

## Why
My current state management relies on loose JSON parsing. As I scale, the risk of silent data corruption in `goals.json` or `experiences.json` increases. By enforcing Pydantic schemas, I move from "hope-based" parsing to "contract-based" state management, ensuring that any malformed data is caught at the boundary before it touches my logic.

## Implementation Steps
1.  Define `StateSchema` (Pydantic models) in a new `bag/schemas.py` file for `goals.json` and `experiences.json`.
2.  Refactor `_parse_gemini_json` to accept a `BaseModel` class and use `model_validate_json` (or `parse_obj`).
3.  Update `load_goals` and `load_experiences` to utilize these schemas, adding a fallback to a "known-good" state if validation fails.
4.  Add a test case in `bag/tests.py` to verify that invalid JSON triggers a graceful recovery rather than a crash.

## Risk
**Failure Mode:** A schema change might break existing legacy data in `goals.json` that doesn't perfectly match the new model.
**Mitigation:** Implement a migration function that attempts to map legacy keys to the new schema before validation, or simply back up the existing file to `rollback_registry` before the first run.

**Confidence Score:** 9/10