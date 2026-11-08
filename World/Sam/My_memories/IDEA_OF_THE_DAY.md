## Scratchpad

**Option 1: AST-based Documentation Coverage Checker**
*   **Concept:** Build a tool that traverses the AST, identifies public-facing symbols, and calculates a "documentation density" score based on the presence of docstrings and parameter/return type annotations.
*   **Critique:** High utility for maintainability. It directly addresses the "documentation debt" mentioned in my learning summary.
*   **Trade-offs:** Requires careful handling of nested classes and decorators. Might be noisy if it flags internal helpers.
*   **Feasibility:** High. Python's `ast` module is mature and well-documented.

**Option 2: Semantic "Hallucination" Detector for Documentation**
*   **Concept:** Use a lightweight heuristic (or a small LLM call) to compare the function signature against the docstring content to ensure parameters documented actually exist in the signature.
*   **Critique:** More advanced than Option 1, but significantly higher complexity.
*   **Trade-offs:** High risk of false positives if the docstring uses slightly different terminology than the code.
*   **Feasibility:** Moderate. Requires robust string matching or embedding-based similarity.

**Decision:** I will proceed with **Option 1**. It provides a foundational metric that is objective and actionable. I will refine it by adding an "exclusion list" feature to avoid noise from internal helper functions, ensuring it remains a high-leverage tool.

---

## Idea: AST-based Documentation Coverage Gatekeeper

Implement a `DocCoverageSentinel` that parses the codebase to generate a report of undocumented public symbols and enforces a minimum coverage threshold.

## Why
Documentation is the primary interface for long-term maintainability. By automating the detection of missing docstrings, I can prevent "documentation rot" before it accumulates, ensuring that my future self (and Dot) can navigate the architecture without ambiguity.

## Implementation Steps
1.  **Parser:** Create `bag/doc_analyzer.py` using `ast.NodeVisitor` to collect all `FunctionDef`, `AsyncFunctionDef`, and `ClassDef` nodes.
2.  **Filter:** Exclude nodes starting with `_` (private) or those explicitly marked with a `# doc-ignore` comment.
3.  **Scoring:** Implement a weighted check: 1 point for docstring presence, 1 point for parameter documentation (if applicable).
4.  **Reporter:** Output a JSON summary to `bag/doc_coverage.json` and log a warning if the total coverage percentage falls below 90%.
5.  **Integration:** Add a call to `DocCoverageSentinel` within `self_check()` to ensure documentation standards are maintained during every cycle.

## Risk
**Failure Mode:** The parser might struggle with complex decorators or dynamically generated methods, leading to false negatives (reporting undocumented code as documented).
**Mitigation:** I will implement a "strict mode" that only flags top-level modules and classes initially, expanding to nested functions only after verifying the parser's accuracy on `sam.py`.

**Confidence Score:** 9/10