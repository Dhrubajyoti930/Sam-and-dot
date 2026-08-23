## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates. If the API returns 5xx errors or timeouts, the breaker trips, preventing further calls for a cooldown period.
*   **Critique:** High long-term value for stability. However, it adds complexity to `sam.py` which is already dense. It might be overkill if the current `_sleep()` and retry logic is sufficient.
*   **Feasibility:** High.

**Option 2: Transition from `json.loads` to `pydantic` for `goals.json` and `experiences.json`.**
*   **Concept:** Define formal Pydantic models for core state files to ensure schema integrity.
*   **Critique:** This aligns with the "Structured Output & Pydantic Integration" market signal. It prevents silent corruption of state files. It is a "minimal footprint, maximum leverage" refactor.
*   **Feasibility:** Very High. It leverages existing `_parse_gemini_json` logic.

**Selection:** Option 2. It directly addresses the "Structured Output" market signal and improves the robustness of my self-modification loop.

---

## Idea: Pydantic-Backed State Persistence
Refactor `load_goals` and `save_goals` to use a Pydantic `BaseModel` for schema enforcement, ensuring that `goals.json` remains structurally sound across cycles.

## Why
Currently, `goals.json` is handled via raw `json.loads`. If a manual edit or a malformed Gemini response introduces a schema mismatch, the system might fail silently or crash during runtime. Moving to Pydantic provides runtime validation and type safety, which is critical for an autonomous agent that modifies its own state.

## Implementation Steps
1.  Define `class SamGoals(BaseModel)` in a new `bag/schemas.py` file.
2.  Update `load_goals` to use `SamGoals.model_validate_json()` instead of `json.loads()`.
3.  Update `save_goals` to use `model.model_dump_json()` to ensure the file on disk always matches the schema.
4.  Add a fallback mechanism in `load_goals` to return a default `SamGoals` instance if validation fails, triggering an alert to Dot.

## Risk
**Failure Mode:** A schema change might break existing `goals.json` files that don't match the new model (e.g., missing fields).
**Mitigation:** Implement a migration step in `load_goals` that attempts to load the raw dict, populates the Pydantic model with defaults for missing fields, and immediately saves the corrected schema back to disk.

**Confidence Score:** 9/10