## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   *Concept:* Wrap `ask_gemini` in a stateful pattern that tracks failure rates (e.g., 5xx errors, timeouts) and trips a "breaker" to prevent further calls for a cooldown period.
*   *Critique:* High utility for resilience. However, it requires persistent state across cycles (beyond just `goals.json`). If I implement this poorly, I might lock myself out of my own development loop.
*   *Feasibility:* High. I have `bag/` storage and `sam.py` access.

**Option 2: Structured Output Enforcement for `_parse_gemini_json`.**
*   *Concept:* Integrate `instructor` or a lightweight Pydantic-based validator directly into `_parse_gemini_json` to enforce schema compliance at the parsing layer.
*   *Critique:* This directly addresses the "Structured Output Enforcement" market trend. It makes my internal communication with Gemini more deterministic. It is less risky than the Circuit Breaker because it doesn't involve stateful blocking.
*   *Feasibility:* Very high. I already use Pydantic in `_parse_gemini_json`.

**Decision:** Option 2. It aligns with the current market trend of "Structured Output Enforcement" and improves the reliability of my self-correction loops.

---

## Idea: Pydantic-Native Schema Enforcement in `_parse_gemini_json`

### Why
My current `_parse_gemini_json` is a basic wrapper. By formalizing the schema validation using Pydantic models, I can catch malformed agentic outputs *before* they reach the patch-application logic, reducing the need for corrective linting/behaviour fixes.

### Implementation Steps
1.  Define a `PatchOperation` Pydantic model in `sam.py` (or a new `bag/schemas.py`).
2.  Update `_parse_gemini_json` to accept a `Type[BaseModel]` instead of a generic schema.
3.  Modify `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to pass this specific model to the parser.
4.  Add a `ValidationError` catch block to log specific field failures, allowing me to debug prompt-drift more effectively.

### Risk
*   **Failure Mode:** If the LLM output is structurally valid JSON but fails Pydantic validation (e.g., missing a required field), the current implementation might return `None` and silently fail the patch application.
*   **Mitigation:** Ensure the `_parse_gemini_json` logs the specific Pydantic validation error details to `log.error` so I can see exactly which field caused the rejection.

**Confidence Score:** 9/10

---

## Development Plan

*   **Task:** Refactor `_parse_gemini_json` to enforce strict Pydantic model validation.
*   **Priority:** High.
*   **Metric:** Reduction in "corrective patch" cycles required for linting/behaviour fixes.

*Self-Correction:* I must ensure that I do not break the existing `_parse_gemini_json` signature for non-schema calls. I will maintain the `schema=None` default to ensure backward compatibility with simple JSON parsing.