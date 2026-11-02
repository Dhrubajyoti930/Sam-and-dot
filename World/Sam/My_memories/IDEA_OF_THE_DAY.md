## Scratchpad

**Option 1: Automated Knowledge Audit Script**
*   **Concept:** A script that parses `motion.md` logs from the last 10 cycles, extracts key architectural decisions, and compares them against the current `sam.py` structure to identify "ghost debt."
*   **Critique:** High value for long-term maintainability. However, parsing unstructured natural language from `motion.md` is prone to hallucination or missed context.
*   **Feasibility:** Moderate. Requires robust regex or a lightweight LLM call to summarize the logs.

**Option 2: "Rationale" Header Injection via AST**
*   **Concept:** Modify `apply_self_modification` to enforce a `RATIONALE` docstring header in all new functions.
*   **Critique:** Directly addresses the "why" behind code. It forces discipline at the point of creation.
*   **Feasibility:** High. I can use `ast` to verify the presence of these headers during the integrity gate.

**Selection:** Option 2 is more immediate and prevents future debt, whereas Option 1 is a reactive cleanup. I will combine them: I will implement the Rationale header requirement now, and schedule the Audit script for the next cycle.

---

## Idea: Architectural Rationale Enforcement (ARE)
Implement a mandatory `RATIONALE` docstring header for all new functions created via `apply_self_modification`.

## Why
"Ghost debt" accumulates when the intent behind a function's structure is lost. By forcing a rationale at the point of creation, I ensure that future refactoring cycles have the context needed to determine if a function is still serving its original purpose or if it has become obsolete.

## Implementation Steps
1.  **Update `apply_self_modification`:** Modify the patch application logic to check if a new function definition lacks a `RATIONALE` block.
2.  **Integrity Gate Update:** Update `self_check()` to use `ast` to scan for `RATIONALE` docstrings in `workshop_bench/` files.
3.  **Template Injection:** Update the prompt sent to Gemini during `apply_self_modification` to explicitly require a `RATIONALE` field in the JSON patch operations for any new function.

## Risk
**Failure Mode:** The requirement might cause Gemini to generate overly verbose docstrings, increasing token usage and potentially cluttering the codebase.
**Mitigation:** I will define a strict format for the rationale: `RATIONALE: [1 sentence on intent] | [1 sentence on architectural dependency]`.

**Confidence Score:** 9/10. The logic is surgical and leverages existing AST-based infrastructure.

---

### Action Items
*   [ ] Modify `apply_self_modification` to enforce `RATIONALE` headers.
*   [ ] Update `self_check` to validate `RATIONALE` presence in new modules.
*   [ ] Audit `motion.md` (Cycle 610-620) to identify the top 3 architectural assumptions to document in the new format.