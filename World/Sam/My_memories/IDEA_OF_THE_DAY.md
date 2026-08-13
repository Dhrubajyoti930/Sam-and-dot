## Scratchpad

**Option 1: Implementing a "Circuit Breaker" for Gemini API Calls**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 500s, truncation loops). If the error rate exceeds a threshold, the system enters an "Open" state, forcing a cooldown period or switching to a fallback model/cached response.
*   **Critique:** High feasibility. It directly addresses the "Calm under failure" trait. However, it adds complexity to `sam.py` and requires persistent state tracking for the circuit status.
*   **Trade-off:** Increases system robustness at the cost of slightly higher latency for state checks.

**Option 2: Integrating "Structured Output" via Instructor for Patch Operations**
*   **Concept:** Refactor `apply_self_modification` and `_lint_fix_with_gemini` to use `instructor` to enforce the JSON schema for patch operations.
*   **Critique:** This aligns perfectly with the "Structured Output Enforcement" market signal. It eliminates the need for `_parse_gemini_json` regex hacks and provides type-safe validation before the patch is even attempted.
*   **Trade-off:** Introduces a new dependency (`instructor`), but significantly reduces the risk of malformed JSON causing `apply_patch_operations` to fail.

**Decision:** Option 2 is superior. It moves Sam toward a more professional, type-safe agentic architecture, reducing the "hallucination" risk in self-modification.

---

## Idea
**Refactor Patch Operations to use `instructor` for Pydantic-validated JSON enforcement.**

## Why
Currently, Sam relies on regex-based parsing (`_parse_gemini_json`) to extract patch operations. This is brittle. By adopting `instructor`, Sam can enforce a strict Pydantic schema for patch operations, ensuring that every `replace`, `delete`, or `insert_after` operation is structurally valid before it ever touches the filesystem. This directly addresses the "Structured Output Enforcement" market signal and improves the reliability of self-modification.

## Implementation Steps
1.  Define a `PatchOperation` Pydantic model in `bag/patch_ops.py` (or a new `bag/schemas.py`) with strict fields for `filename`, `operation`, `old`, and `new`.
2.  Update `apply_self_modification` and `_lint_fix_with_gemini` to use `instructor.patch(CLIENT).chat.completions.create(...)` with the `response_model` parameter.
3.  Remove the regex-based `_parse_gemini_json` logic in favor of the validated Pydantic object.
4.  Update `apply_patch_operations` to accept the validated Pydantic objects directly.

## Risk
**Failure Mode:** The `instructor` library might introduce a dependency conflict or require a specific version of `pydantic` that clashes with the current environment.
**Mitigation:** Perform a dry-run check of the `instructor` import and schema validation in a temporary script before committing the change to `sam.py`.
**Confidence Score:** 8/10. The logic is sound, but dependency management is always a variable.