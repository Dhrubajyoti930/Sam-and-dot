## Scratchpad

**Option 1: Implement Envelope Encryption for `bag/` secrets.**
*   **Concept:** Integrate a KMS-based envelope encryption pattern to protect sensitive data stored in `bag/`.
*   **Critique:** High security value, but requires external dependencies (KMS provider) or a local mock implementation. If I use a cloud provider, I introduce latency and dependency on network/IAM. If I use a local mock, it’s security theater.
*   **Feasibility:** Moderate. Requires careful handling of the DEK lifecycle.

**Option 2: AST-based "Lint-to-Patch" Automation.**
*   **Concept:** Instead of relying on Gemini to guess patch operations from raw lint output, build a local utility that uses `ast` to identify the exact line/node of an `F821` (undefined name) or `F401` (unused import) and generate the patch operation locally.
*   **Critique:** This moves logic from the LLM (unreliable) to code (deterministic). It significantly reduces the "Gemini-as-a-patcher" failure rate.
*   **Feasibility:** High. I already have `_outline` and `apply_patch_operations`.

**Selection:** Option 2. It directly addresses the "fragile patching" concern mentioned in my recent experiences and aligns with my goal of moving toward deterministic, autonomous maintenance.

---

## Idea: Deterministic AST-based Lint Remediation

Develop a local utility `bag/lint_remediator.py` that parses `ruff` output and uses Python’s `ast` module to locate and resolve `F401` (unused imports) and `F821` (undefined names) without invoking Gemini.

## Why
My current reliance on Gemini to interpret lint errors is a point of failure. LLMs often hallucinate line numbers or context strings when patching. By using `ast` to identify the exact node location of an unused import or an undefined variable, I can generate the `patch_op` JSON locally, ensuring 100% accuracy in the "old" string anchor.

## Implementation Steps
1.  **Create `bag/lint_remediator.py`:** Implement a function `get_ast_patch(file_path, error_type, line_no)` that parses the file into an AST.
2.  **Logic for F401:** Use `ast.walk` to find the `Import` or `ImportFrom` node at the specified line and return a `delete` operation.
3.  **Logic for F821:** Identify the scope of the undefined name and suggest an `insert_after` for the missing import (if the name is a known standard library module).
4.  **Integration:** Update `_lint_fix_with_gemini` in `sam.py` to first attempt `lint_remediator.get_ast_patch`. Only fallback to Gemini if the local remediator returns no result.

## Risk
**Failure Mode:** The AST might not map perfectly to the source if the file has complex formatting or multiple imports on one line.
**Mitigation:** If the AST node span doesn't match the expected line, the remediator will return `None`, triggering the existing Gemini fallback.
**Confidence Score:** 8/10. The AST module is robust, and the fallback ensures no regression if the local logic fails.