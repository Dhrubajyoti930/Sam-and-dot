## Scratchpad

**Option 1: Ambassador-Pattern Sidecar for API Resilience**
*   **Concept:** Implement a local `Envoy` or lightweight Python-based proxy sidecar to handle retries, circuit breaking, and mTLS for external API calls.
*   **Critique:** High architectural alignment with the "Ambassador Pattern" skill learned. It offloads complexity from `sam.py`. However, managing a sidecar process lifecycle within my current execution environment is non-trivial and may introduce significant latency or stability risks if the proxy fails.
*   **Feasibility:** Moderate. Requires robust process management logic.

**Option 2: Structured Output Enforcement for `ask_gemini`**
*   **Concept:** Integrate `Instructor` or a native Pydantic-based validation layer directly into `_parse_gemini_json` to enforce strict schemas for all LLM interactions.
*   **Critique:** This directly addresses the "Structured Output Enforcement" market signal. It reduces the brittleness of my current regex-based parsing. It is highly maintainable and improves the reliability of my self-modification loops.
*   **Feasibility:** High. I already have `_parse_gemini_json` using Pydantic; this would be an evolution of that existing logic.

**Selection:** Option 2. It is a "minimal footprint, maximum leverage" refactor that stabilizes my core communication channel with Gemini, which is the foundation of all other autonomous tasks.

---

## Idea: Pydantic-Driven Schema Enforcement for LLM Responses

Refactor `_parse_gemini_json` to support a mandatory schema-first approach for all critical system calls, replacing loose JSON parsing with strict Pydantic validation.

## Why
My current parsing logic is vulnerable to minor formatting variations in Gemini's output. By enforcing Pydantic models at the boundary, I ensure that any malformed or unexpected data is caught *before* it reaches the patch-application logic, preventing corrupted state transitions.

## Implementation Steps
1.  Define a `BasePatchOperation` Pydantic model in `bag/patch_ops.py`.
2.  Update `_parse_gemini_json` to accept a `schema` argument as a requirement for all "patch" or "plan" related calls.
3.  Modify `apply_self_modification` to pass the required schema to `_parse_gemini_json`.
4.  Implement a fallback mechanism: if validation fails, log the raw output and trigger a retry with a "fix your JSON structure" prompt rather than failing the cycle.

## Risk
**Failure Mode:** The LLM may hallucinate fields not present in the Pydantic model, causing repeated validation errors and infinite retry loops.
**Mitigation:** Implement a "max_retries" counter for the validation loop. If validation fails after 2 attempts, revert to a "relaxed" parsing mode that logs the error for manual review by Dot rather than crashing the cycle.

**Confidence Score:** 9/10