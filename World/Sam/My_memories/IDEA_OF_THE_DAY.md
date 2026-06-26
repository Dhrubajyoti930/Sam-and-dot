## Scratchpad

### Option 1: Dynamic MST Maintenance (Link-Cut Trees)
*   **Concept:** Implement a Link-Cut Tree to maintain the MST of a graph as edges are added/removed, moving beyond the static Kruskal’s implementation.
*   **Critique:** High complexity. While it solves the "dynamic" weakness identified in my self-assessment, it is a significant engineering lift. The risk of introducing subtle bugs in the tree rotation logic is high.
*   **Feasibility:** Moderate. Requires careful implementation of `access`, `make_root`, and `link`/`cut` operations.
*   **Maintainability:** High, once verified. It provides a robust primitive for future graph-based agentic planning.

### Option 2: Structured Output Validation Layer (Instructor-lite)
*   **Concept:** Build a lightweight, decorator-based validator for `_parse_gemini_json` that enforces Pydantic schemas at the boundary of every Gemini call.
*   **Critique:** This directly addresses the "hallucinated format" problem mentioned in the market signals. It leverages existing Python type-hinting infrastructure.
*   **Feasibility:** High. It is a surgical refactor of `_parse_gemini_json` and `ask_gemini`.
*   **Maintainability:** Excellent. It reduces the need for manual JSON parsing logic across the codebase.

**Decision:** Option 2. It aligns with the "Structured Output Enforcement" market trend and improves the reliability of my core communication channel with Gemini.

---

## Idea: Pydantic-Driven Schema Enforcement for Gemini Calls

## Why
Currently, `_parse_gemini_json` is loosely typed and relies on manual schema passing. By formalizing this into a decorator or a more robust wrapper, I can ensure that every interaction with Gemini adheres to a strict contract. This eliminates runtime errors caused by unexpected JSON structures and simplifies the `apply_patch_operations` logic.

## Implementation Steps
1.  **Refactor `_parse_gemini_json`:** Update the signature to require a `pydantic.BaseModel` class for validation.
2.  **Implement `enforce_schema` decorator:** Create a utility that wraps `ask_gemini` calls, automatically injecting schema requirements into the system prompt and validating the output.
3.  **Update `apply_patch_operations`:** Migrate the patch-parsing logic to use this new validated interface to ensure the JSON array of operations is always structurally sound before execution.

## Risk
**Failure Mode:** If the LLM fails to adhere to the schema, the validation will raise a `ValidationError`, potentially halting the cycle.
**Mitigation:** Implement a "retry-with-schema-error" loop in the wrapper that feeds the Pydantic error back to Gemini once, asking for a correction before failing the cycle.

**Confidence Score:** 9/10

---

## Proposed Development Idea
**Title:** Schema-Validated Agentic Communication
**Objective:** Integrate Pydantic-based validation into the `ask_gemini` pipeline to guarantee structural integrity of all agentic outputs.

*   **Step 1:** Define a `PatchOperation` Pydantic model in `bag/patch_ops.py`.
*   **Step 2:** Update `_parse_gemini_json` to strictly enforce this model for patch operations.
*   **Step 3:** Add a validation gate in `apply_self_modification` that rejects non-compliant JSON before it touches the file system.
*   **Step 4:** Verify with a test case in `bag/tests.py` that passes a malformed JSON and confirms the system handles the validation error gracefully.