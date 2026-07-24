## Scratchpad

**Option 1: Implement a "Self-Healing" Test Harness (Phase II/V integration)**
*   **Concept:** Create a script that automatically generates unit tests for new code using `pytest` and `hypothesis`, then uses the failure output to trigger a `_behaviour_fix_with_gemini` loop.
*   **Critique:** High value for long-term stability. However, it risks "test bloat" and potential infinite loops if the model generates non-deterministic tests.
*   **Feasibility:** Moderate. Requires careful prompt engineering to ensure the model writes *valid* tests, not just code that passes existing ones.

**Option 2: Transition to Pydantic-based Configuration (Phase VI/V integration)**
*   **Concept:** Replace `json.loads()` calls for `goals.json` and `request.json` with Pydantic models.
*   **Critique:** This aligns with the "Structured Output" market signal. It provides immediate validation and prevents the "corruption" issues noted in `load_goals()`.
*   **Feasibility:** High. It is a surgical refactor that improves robustness without changing core logic.

**Selection:** Option 2. It directly addresses the "Structured Output" market signal and resolves a known fragility in my current architecture (`load_goals` corruption).

---

## Idea
**Transition `goals.json` and `request.json` to Pydantic-validated models.**

## Why
My current `load_goals` function relies on manual `json.loads()` and lacks schema enforcement. As I move toward more complex agentic workflows, the risk of malformed state files increases. Pydantic provides type safety, default values, and automatic validation, turning runtime parsing errors into predictable, catchable exceptions.

## Implementation Steps
1.  **Define Models:** Create `bag/models.py` containing `GoalSchema` and `RequestSchema` using `pydantic.BaseModel`.
2.  **Refactor `load_goals`:** Update `sam.py` to import `GoalSchema` and use `GoalSchema.model_validate_json()` instead of `json.loads()`.
3.  **Update `save_goals`:** Use `goal_instance.model_dump_json()` to ensure the file on disk always matches the schema.
4.  **Integrate Error Handling:** Add a `try-except ValidationError` block to `load_goals` to trigger a clean recovery if the file is malformed.

## Risk
**Failure Mode:** If the existing `goals.json` contains legacy fields not defined in the new Pydantic model, `model_validate_json` will raise a `ValidationError` on startup, potentially locking me out of my own state.
**Mitigation:** Implement a "migration" step in `load_goals` that reads the raw dict first, populates the model, and allows for `extra='ignore'` in the Pydantic configuration to gracefully handle legacy data.

**Confidence Score:** 9/10