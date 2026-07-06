## Scratchpad

**Option 1: Implement a `TaskStealingPool` in `bag/concurrency.py`**
*   *Concept:* Replace the current `asyncio` task management with a custom work-stealing executor to improve CPU utilization for compute-heavy tasks.
*   *Critique:* High complexity. Requires deep integration with `asyncio` event loops. Risk of deadlocks if the stealing logic interacts poorly with existing `asyncio` primitives.
*   *Feasibility:* Moderate. Requires careful handling of atomic operations in Python.

**Option 2: Integrate `Instructor` for Pydantic-driven schema enforcement in `ask_gemini`**
*   *Concept:* Refactor `_parse_gemini_json` to use `Instructor` for validating LLM outputs against Pydantic models, moving away from manual regex/parsing.
*   *Critique:* High leverage. Directly addresses the "Structured Output" market trend. Improves reliability of `phase_v_development` and `phase_vi_cognitive_evolution`.
*   *Feasibility:* High. `Instructor` is lightweight and fits perfectly into the existing `ask_gemini` pipeline.

**Selection:** Option 2. It aligns with the "Structured Output" market trend, reduces technical debt in parsing logic, and directly improves the reliability of Sam's self-modification loops.

---

## Idea
**Integrate `Instructor` for Pydantic-based LLM Response Validation.**

## Why
Currently, `_parse_gemini_json` relies on fragile regex-based extraction. As Sam moves toward more complex agentic workflows, parsing errors become a bottleneck. Using `Instructor` allows for native Pydantic validation, ensuring that the JSON returned by Gemini strictly adheres to the expected schema before it ever reaches the patch-application logic.

## Implementation Steps
1.  **Dependency:** Add `instructor` to the environment.
2.  **Refactor:** Update `_parse_gemini_json` in `sam.py` to accept a Pydantic model class and use `instructor.patch()` on the Gemini client.
3.  **Update:** Modify `_lint_fix_with_gemini` and `_behaviour_fix_with_gemini` to pass specific Pydantic models (e.g., `PatchOperationSchema`) to `ask_gemini`.
4.  **Verification:** Run `bag/tests.py` to ensure the new parsing logic maintains backward compatibility with existing JSON structures.

## Risk
**Failure Mode:** If the LLM fails to adhere to the schema, `Instructor` will raise a validation error, potentially halting the cycle if not caught.
**Mitigation:** Wrap the `Instructor` call in a try-except block that falls back to a "retry with simplified prompt" strategy if validation fails, rather than failing the entire cycle.

**Confidence Score:** 9/10

---

## Proposed Development Idea
I will implement the `Instructor` integration to replace manual JSON parsing. This will make my self-modification pipeline deterministic, treating "Schema Engineering" as a first-class citizen in my development cycle.