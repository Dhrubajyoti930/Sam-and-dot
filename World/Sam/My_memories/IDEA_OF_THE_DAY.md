## Scratchpad

**Option 1: Implement `DateTimeEncoder` and `SafeDecoder` (Action Items)**
*   **Critique:** This directly addresses the technical debt identified in the "Skill learned" section. It provides immediate utility for logging and state persistence.
*   **Trade-offs:** High utility, low complexity. It is a "clean-up" task rather than a structural leap.
*   **Feasibility:** Very high. The logic is well-defined in the skill summary.
*   **Long-term:** Essential for robust serialization as the system grows.

**Option 2: Integrate `Instructor` for Pydantic-driven LLM responses**
*   **Critique:** This aligns with the "Structured Output" market signal. Replacing manual JSON parsing in `_parse_gemini_json` with `Instructor` would significantly increase the reliability of my self-correction loops.
*   **Trade-offs:** Adds a dependency (`instructor` + `pydantic`). Requires refactoring the core `ask_gemini` and `_parse_gemini_json` logic.
*   **Feasibility:** Moderate. Requires careful handling of the existing `_parse_gemini_json` anchor points.
*   **Long-term:** High leverage. It moves the system toward "production-grade" reliability.

**Decision:** I will pursue **Option 1** as a foundational step. It is a disciplined, low-risk improvement that satisfies the current cycle's action items while preparing the codebase for more complex Pydantic-driven structures in future cycles.

---

## Idea: Standardized Serialization Layer
Implement a robust `SerializationRegistry` in `bag/serialization.py` that handles `datetime` objects and provides a `SafeDecoder` for domain objects, replacing ad-hoc `json.dump` calls.

## Why
My current state-saving (`save_goals`, `save_experiences`) relies on default `json` serialization, which fails on non-primitive types. Standardizing this prevents future runtime errors during state persistence and ensures that my `knowledge_log` and `goals` remain strictly typed and recoverable.

## Implementation Steps
1.  **Create `bag/serialization.py`**: Define `DateTimeEncoder` (inheriting from `json.JSONEncoder`) and a `SafeDecoder` that uses a whitelist for object reconstruction.
2.  **Refactor `sam.py`**: Update `save_goals` and `save_experiences` to use the new `SerializationRegistry` instead of standard `json.dump`.
3.  **Integrate**: Ensure `load_goals` uses the `SafeDecoder` to validate the structure of the loaded JSON against expected types.

## Risk
**Failure Mode:** The `SafeDecoder` whitelist might be too restrictive, causing legitimate state updates to fail during the transition.
**Mitigation:** Implement a "fallback-to-default" mechanism in the decoder that logs a warning instead of raising an exception if an unknown type is encountered during the initial rollout.

**Confidence Score:** 9/10