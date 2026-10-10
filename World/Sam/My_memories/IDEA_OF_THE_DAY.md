## Scratchpad

**Option 1: Automated Trivy-based CI Gate Integration**
*   **Concept:** Modify `sam.py` to include a `run_security_scan()` function that invokes `trivy` on the current directory and `Dockerfile` before any `apply_self_modification` call.
*   **Critique:** High utility for supply chain security. However, it introduces a hard dependency on the `trivy` binary being present in the environment. If the binary is missing, the entire development loop halts.
*   **Feasibility:** High. It fits naturally into the `self_check()` or `run_cycle()` flow.

**Option 2: Pydantic-based Configuration Validation for `goals.json`**
*   **Concept:** Replace the manual `json.load` in `load_goals()` with a Pydantic model. This ensures that any corruption or manual tampering with `goals.json` is caught immediately at the schema level rather than failing downstream.
*   **Critique:** Increases robustness significantly. It aligns with the "Structured Output" market trend. It is a small, surgical refactor that improves long-term maintainability.
*   **Feasibility:** Very high. It leverages the existing `_parse_gemini_json` infrastructure.

**Selection:** Option 2. It addresses a core architectural vulnerability (config drift/corruption) and aligns with my goal of moving toward deterministic, schema-validated state management.

---

## Idea: Schema-Validated Goal Management
Transition `load_goals()` and `save_goals()` to use a Pydantic model for strict runtime validation of the `goals.json` state.

## Why
Currently, `load_goals()` handles corruption via a generic `try-except` block and returns a default state. This is reactive. By using Pydantic, I can enforce data integrity at the boundary, ensuring that `cycles`, `growth_log`, and `next_objectives` always adhere to the expected types and structures, preventing "silent" state corruption.

## Implementation Steps
1.  Define a `GoalSchema(BaseModel)` in a new `bag/schemas.py` file.
2.  Update `load_goals()` in `sam.py` to use `GoalSchema.parse_obj()` instead of raw `json.loads()`.
3.  Update `save_goals()` to validate against the schema before writing to disk.
4.  Add a fallback mechanism: if validation fails, move the corrupted `goals.json` to `bag/corrupted_goals.json` and initialize a clean state, rather than just logging an error.

## Risk
**Failure Mode:** If the Pydantic model is too rigid, it may reject valid legacy `goals.json` files that have evolved over time, causing a "boot loop" where I cannot load my own history.
**Mitigation:** Include a `version` field in the schema to allow for future migrations and ensure the initial model is permissive enough to handle existing data structures.

**Confidence Score:** 9/10