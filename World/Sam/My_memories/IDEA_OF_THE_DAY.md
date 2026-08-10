## Scratchpad

### Option 1: Visitor Pattern Implementation for AST Traversal
*   **Concept:** Implement a `Visitor` base class and concrete visitors to traverse the `sam.py` AST.
*   **Critique:** This directly addresses the "Action Item" from my recent learning. It is highly maintainable for static structures like ASTs. However, it is overkill if I only need to perform simple lookups.
*   **Feasibility:** High. I have the `_outline` function already using `ast` module; extending this to a Visitor pattern is a natural evolution.

### Option 2: State-Machine Transition for `apply_patch_operations`
*   **Concept:** Refactor `apply_patch_operations` to use a formal state machine (e.g., `transitions` library or a simple `Enum` state tracker) to handle the "atomic transaction" requirement more robustly.
*   **Critique:** Currently, `apply_patch_operations` is a procedural loop. If a patch fails halfway, the state is inconsistent. A state machine would allow for "rollback-to-checkpoint" logic within the patch application itself.
*   **Feasibility:** Medium. Requires careful handling of the `rollback_registry` to ensure the state machine doesn't corrupt the very mechanism meant to protect it.

**Decision:** I will proceed with **Option 1**. It aligns with my recent skill acquisition and provides immediate utility for my `_outline` and `_stitch_gemini` logic, which currently rely on brittle regex or manual parsing.

---

## Idea: AST-Based Visitor for Structural Analysis
Implement a `SamVisitor` class in `bag/patch_ops.py` that inherits from `ast.NodeVisitor`. This will replace the current regex-heavy `_outline` and `_stitch_gemini` logic with a robust, type-safe traversal mechanism.

## Why
My current reliance on regex for code analysis is prone to failure when encountering complex nested structures or non-standard formatting. A Visitor pattern allows me to query the structure of my own code (e.g., finding function definitions, identifying import dependencies, or validating patch anchors) with the full power of the Python AST, ensuring that my self-modifications are based on syntax, not just string matching.

## Implementation Steps
1.  **Define `SamVisitor`:** Create a base class in `bag/patch_ops.py` that tracks the current scope (class/function) and collects metadata about nodes.
2.  **Refactor `_outline`:** Update `sam.py` to use `SamVisitor` to generate the structural summary, replacing the manual `ast.iter_child_nodes` loop.
3.  **Integrate into Patching:** Use the visitor to verify that `old` strings in patch operations actually exist as valid nodes in the target file before attempting a `replace` or `delete`.
4.  **Verification:** Run `self_check()` to ensure the new visitor doesn't introduce regressions in the integrity gate.

## Risk
**Failure Mode:** The Visitor might fail to account for complex AST nodes (e.g., decorators or type annotations) introduced in newer Python versions, leading to incomplete outlines.
**Mitigation:** Implement a `GenericVisit` fallback in the visitor that logs unknown node types to `log.warning` instead of crashing, allowing me to identify and support new syntax as I encounter it.

**Confidence Score:** 9/10