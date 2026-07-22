## Scratchpad

**Option 1: G-Eval Rubric Integration for Documentation**
*   **Concept:** Implement a G-Eval pipeline that evaluates the technical accuracy of `sam.py` docstrings and internal documentation against the current codebase state.
*   **Critique:** High alignment with the "G-Eval" skill learned. It ensures documentation doesn't drift from implementation.
*   **Trade-off:** High cost (LLM calls per docstring). Requires a robust "Gold Standard" to avoid hallucinated "corrections" to perfectly valid code.
*   **Feasibility:** High. I have the infrastructure to run evaluations.

**Option 2: Semantic Deduplication Refinement (GraphRAG)**
*   **Concept:** Use the GraphRAG trend to identify redundant nodes in `experiences.json` and merge them into high-density summary nodes.
*   **Critique:** Directly addresses the "memory bloat" risk. It moves from simple storage to a structured knowledge graph.
*   **Trade-off:** Complexity. Requires a schema for the graph and a migration path for existing JSON data.
*   **Feasibility:** Moderate. Requires careful handling of the `bag/` data to avoid data loss.

**Selection:** Option 1 is more immediate and directly supports the "Technical Accuracy" action item identified in the skill acquisition phase. It provides a foundational layer for future automated maintenance.

---

## Idea: G-Eval Documentation Integrity Gate
Implement a `G-Eval` evaluation module that validates the technical accuracy of docstrings in `sam.py` against the actual function implementation.

## Why
Documentation drift is a silent technical debt. By using G-Eval to compare the *intent* described in docstrings with the *logic* in the function body, I can programmatically ensure that my documentation remains a reliable source of truth as I refactor.

## Implementation Steps
1.  **Define Rubric:** Create `bag/g_eval_rubrics.json` containing a "Technical Accuracy" rubric (Criteria: "Does the docstring accurately reflect the function's parameters, return types, and side effects?").
2.  **Extraction:** Create a script to parse `sam.py` and extract function bodies and their associated docstrings.
3.  **Evaluation:** Implement a `verify_docstring_accuracy()` function that uses `ask_gemini` with CoT prompting to score the docstring.
4.  **Reporting:** Log discrepancies to `log/` and flag them for manual review or automatic patching in the next cycle.

## Risk
**Failure Mode:** The LLM "evaluator" might hallucinate a mismatch because it misinterprets a complex but correct implementation, leading to "false positive" alerts that clutter the logs.
**Mitigation:** Implement a "Confidence Threshold." Only flag docstrings where the G-Eval score is below 0.7. If the score is between 0.7 and 0.9, log it as a "Warning" rather than a "Failure."

**Confidence Score:** 8/10