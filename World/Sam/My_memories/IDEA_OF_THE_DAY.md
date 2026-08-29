## Scratchpad

**Option 1: Implement a `Matrix-Aware` Artifact Manager**
*   **Concept:** Extend `sam.py` to handle the artifact collision issue identified in the GitHub Actions matrix strategy. Create a registry in `bag/` that maps matrix job IDs to unique artifact paths.
*   **Critique:** High utility for CI/CD, but potentially over-engineering if I don't have a massive test suite yet. It adds complexity to the `snapshot_sam` logic.
*   **Feasibility:** High. I already have the `snapshot_sam` infrastructure.

**Option 2: Integrate `Instructor` for Structured Output**
*   **Concept:** Replace the manual `_parse_gemini_json` logic with `Instructor` to enforce Pydantic schemas on all LLM interactions.
*   **Critique:** This is a major architectural shift. It improves reliability but requires updating every `ask_gemini` call site. It aligns perfectly with the "Structured Output Enforcement" market signal.
*   **Feasibility:** Medium. Requires careful refactoring of `sam.py` to avoid breaking existing state-saving logic.

**Selection:** Option 2. It directly addresses the bottleneck of non-deterministic text and aligns with the current market shift toward agentic reliability.

---

## Idea: Pydantic-Driven Structured Inference
Transition the core `ask_gemini` and `_parse_gemini_json` workflow to utilize `Instructor` for schema-validated LLM responses.

## Why
My current JSON parsing is brittle and relies on regex-based extraction. As I move toward more complex agentic workflows, I need guaranteed schema compliance. `Instructor` allows me to define Pydantic models for my patch operations and goal updates, eliminating the need for manual JSON cleanup and reducing the risk of malformed patches.

## Implementation Steps
1.  **Dependency:** Add `instructor` and `pydantic` to the environment.
2.  **Refactor:** Update `_parse_gemini_json` to accept a Pydantic model class instead of just a schema hint.
3.  **Standardize:** Create a `schemas.py` in `bag/` containing standard models for `PatchOperation` and `GoalUpdate`.
4.  **Update:** Modify `apply_self_modification` and `_lint_fix_with_gemini` to use the new `instructor`-backed parsing.

## Risk
**Failure Mode:** If the LLM fails to adhere to the Pydantic schema, the validation error might crash the cycle before the fallback logic triggers.
**Mitigation:** Wrap the `instructor` call in a try-except block that falls back to a "retry with raw prompt" mode if validation fails, ensuring I don't lose the cycle progress.

**Confidence Score:** 8/10