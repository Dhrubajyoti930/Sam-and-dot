## Scratchpad

**Option 1: Implementing a `StreamManager` for SSE.**
*   **Concept:** Build a robust `StreamManager` class in `bag/` that wraps `ReadableStream` and handles the `X-Accel-Buffering` requirements, reconnection logic, and event-type dispatching.
*   **Critique:** High utility for real-time agent feedback. It aligns with the "Agentic Orchestration" trend. However, it adds complexity to the `bag/` directory.
*   **Feasibility:** High. The protocol is well-understood, and the `fetch` API implementation is standard.

**Option 2: Integrating `Instructor` for Schema-Validated Patching.**
*   **Concept:** Refactor `apply_self_modification` to use `Instructor` for parsing the JSON patch operations. Currently, I rely on `_parse_gemini_json` which is brittle if the model hallucinates keys.
*   **Critique:** This directly improves the reliability of my self-modification loop (Phase V/VI). It reduces the risk of malformed patches causing integrity gate failures.
*   **Feasibility:** Very high. I already have `pydantic` available.

**Decision:** I will proceed with **Option 2**. My self-modification loop is the most critical path; hardening it with Pydantic/Instructor ensures that my "autonomous developer" loop remains stable as I scale complexity.

---

## Idea: Hardening Self-Modification with Pydantic-Instructor

Refactor the `apply_self_modification` and `_lint_fix_with_gemini` pipelines to use a strict Pydantic model for patch operations, replacing the current loose JSON parsing.

## Why
My current `_parse_gemini_json` is a heuristic-based fallback. By defining a `PatchOperation` Pydantic model, I can force Gemini to adhere to a strict schema. This eliminates "missing key" errors and ensures that the `apply_patch_operations` function receives validated data, significantly reducing the frequency of integrity gate failures.

## Implementation Steps
1.  Define `PatchOperation` and `PatchPlan` Pydantic models in a new `bag/schemas.py`.
2.  Update `_parse_gemini_json` to optionally accept these models for strict validation.
3.  Modify `apply_self_modification` to pass the `PatchPlan` model to the parser.
4.  Update the prompt in `_lint_fix_with_gemini` to explicitly request the JSON structure matching the new Pydantic schema.

## Risk
**Failure Mode:** If the model struggles to map complex code blocks into the strict Pydantic schema (e.g., escaping issues in the `new` string), the patch might fail to generate entirely.
**Mitigation:** I will include a "raw" fallback in the parser that logs a warning if validation fails, allowing me to inspect the output before it hits the integrity gate.

**Confidence Score:** 9/10

---

## 1% Metric
I will measure the **"Integrity Gate Pass Rate"** for self-modification patches. My goal is to reduce the number of corrective lint/behaviour patches required per cycle by 20% by ensuring the initial patch plan is schema-valid.