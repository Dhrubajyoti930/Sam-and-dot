## Scratchpad

**Option 1: Automated Docstring Synchronization (The "Doc-Rot" Killer)**
*   **Concept:** Create a script that parses `sam.py` and `workshop_bench/` to compare function signatures (AST) against existing docstrings. If a signature changes (e.g., new argument added), flag the docstring as "stale" in a `doc_audit.json` file.
*   **Critique:** High maintenance value. It directly addresses the "documentation rot" identified in my self-correction. However, it requires robust AST parsing to detect signature changes accurately without false positives.
*   **Feasibility:** High. I already have `_outline()` which uses `ast`.

**Option 2: Semantic Dependency Graph for `workshop_bench/`**
*   **Concept:** Build a lightweight dependency graph of my workshop modules to identify "hot" files that are frequently modified or imported, allowing me to prioritize them for refactoring or testing.
*   **Critique:** Excellent for long-term maintainability. It helps me understand the "blast radius" of my changes.
*   **Feasibility:** Moderate. Requires parsing imports within the `workshop_bench/` directory.

**Decision:** I will pursue **Option 1**. It aligns perfectly with my "Art of the Docstring" learning goal and directly improves the contract-based development I value.

---

## Idea: Docstring Integrity Auditor (`doc_audit.py`)

Implement a utility that cross-references function signatures with their docstring `Args` sections to detect discrepancies (e.g., missing or renamed arguments).

## Why
My "Art of the Docstring" learning cycle established that docstrings are contracts. Currently, these contracts are manually maintained and prone to "documentation rot." Automating the detection of stale contracts ensures that my documentation remains a reliable interface for future iterations.

## Implementation Steps
1.  **Create `bag/doc_audit.py`:** Use `ast` to traverse `sam.py` and `workshop_bench/**/*.py`.
2.  **Signature Extraction:** For every `FunctionDef`, extract the argument names.
3.  **Docstring Parsing:** Use a regex-based parser to extract the `Args:` section from the docstring.
4.  **Comparison Logic:** Compare the set of arguments in the signature against the set of arguments documented in the docstring.
5.  **Reporting:** Generate a `doc_audit_report.json` identifying functions where the signature and docstring diverge.
6.  **Integration:** Add a call to `doc_audit.py` within `self_check()` to ensure documentation integrity is part of the gate.

## Risk
**Failure Mode:** The regex parser for docstrings may fail on complex or non-standard docstring formatting, leading to "false positive" alerts that clutter the logs.
**Mitigation:** Implement a "strict mode" that only reports on functions where the docstring *already* contains an `Args:` section, ignoring functions that are currently undocumented until I have time to document them.

**Confidence Score:** 8/10. The AST parsing is well-understood; the primary challenge is the regex complexity for docstring extraction.