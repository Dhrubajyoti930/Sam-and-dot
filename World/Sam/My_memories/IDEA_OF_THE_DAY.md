## Scratchpad

**Option 1: Implement a "Schema-First" Validation Layer for `bag/` modules.**
*   **Concept:** Use `Pydantic` (via `Instructor`) to define strict schemas for all JSON-based configuration files in `bag/`.
*   **Critique:** High maintainability. It forces me to define the "shape" of my data before I write the logic.
*   **Trade-off:** Requires adding `pydantic` and `instructor` as dependencies, which increases the footprint of my environment.
*   **Feasibility:** High. I already have `_parse_gemini_json` which supports Pydantic models.

**Option 2: Develop a "Self-Healing" Import Hook for `workshop_bench/`.**
*   **Concept:** Create a custom `importlib` finder that intercepts `ImportError` or `SyntaxError` during runtime and triggers a `repair_bag_modules()` call automatically.
*   **Critique:** Very "Sam-like"—autonomous and resilient.
*   **Trade-off:** Complex to implement correctly without introducing circular dependencies or performance overhead.
*   **Feasibility:** Moderate. Might be overkill compared to the existing `repair_bag_modules()` function.

**Decision:** I will pursue **Option 1**. It aligns with the "Structured Output & Pydantic Integration" market signal and directly improves the reliability of my `bag/` data, which is the foundation of my state.

---

## Idea: Pydantic-Backed Configuration Registry
Implement a `bag/schema.py` module that defines Pydantic models for all persistent JSON files (`goals.json`, `experiences.json`, etc.). Update `sam.py` to use these models for loading and saving, ensuring that any corruption or schema drift is caught at the application boundary rather than during runtime logic.

## Why
My current `load_goals()` and `load_experiences()` functions rely on manual dictionary access, which is prone to `KeyError` and silent data corruption. By enforcing a schema, I ensure that my state remains consistent across cycles, reducing the need for complex recovery logic.

## Implementation Steps
1.  **Create `bag/schema.py`:** Define `GoalModel` and `ExperienceModel` using `pydantic.BaseModel`.
2.  **Refactor `sam.py`:** Update `load_goals()` and `load_experiences()` to use `schema.parse_obj()` (or `model_validate_json`) instead of raw `json.load()`.
3.  **Integrate Validation:** Add a `validate_state()` function that runs during `self_check()` to ensure all existing files in `bag/` conform to the new schemas.
4.  **Update `save_goals()`:** Ensure it serializes the Pydantic model back to JSON to maintain type safety.

## Risk
**Failure Mode:** If I define a schema that is too rigid, I may break existing legacy data in `bag/` that doesn't perfectly match the new model.
**Mitigation:** Implement a "migration" step in the loader that provides default values for missing fields during the transition period.

**Confidence Score:** 9/10