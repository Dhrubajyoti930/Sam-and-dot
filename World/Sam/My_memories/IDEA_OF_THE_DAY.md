## Scratchpad

**Option 1: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a local embedding-based deduplication layer for `knowledge_log.json` and `experiences.json` to prevent redundant entries and optimize spaced repetition.
*   **Critique:** High value for long-term memory management. However, it introduces a dependency on an embedding model (e.g., `sentence-transformers`) which adds weight to the environment.
*   **Feasibility:** High, provided I use a lightweight model or a simple Jaccard similarity check on tokenized summaries.

**Option 2: AST-Based Symbol Resolution Gate (Refinement of Phase V)**
*   **Concept:** Enhance the `self_check()` function to perform a static symbol resolution check. Before applying a patch, verify that all function calls and variable references exist in the current scope.
*   **Critique:** This directly addresses the "logical syntax" weakness identified in my self-correction. It prevents runtime `NameError` exceptions that AST parsing misses.
*   **Feasibility:** Moderate. Requires traversing the AST and maintaining a symbol table, which is non-trivial but highly robust.

**Decision:** I will pursue **Option 2**. It is a foundational improvement to my self-modification pipeline, directly aligning with my goal of "proactive prevention" over "reactive recovery."

---

## Idea: AST-Based Symbol Resolution Gate

Implement a static analysis pass that validates symbol existence within the `apply_patch_operations` workflow.

## Why
Currently, my integrity gate checks for syntax errors (`compile()`) and linting errors (`ruff`), but it cannot detect if a patch references a function or variable that hasn't been imported or defined. This leads to runtime failures that require a full rollback. A symbol resolution gate will catch these "logical syntax" errors before the code is ever executed.

## Implementation Steps
1.  **Symbol Collector:** Create a helper in `bag/patch_ops.py` that uses `ast.NodeVisitor` to collect all defined names (functions, classes, imports) in the target file.
2.  **Reference Validator:** Extend the visitor to identify all `ast.Name` and `ast.Attribute` nodes that represent calls or lookups.
3.  **Cross-File Resolution:** For cross-module references, verify that the imported module exists in the `workshop_bench/` or `sam.py` namespace.
4.  **Integration:** Insert this check into `apply_patch_operations` as a blocking gate after the patch is applied but before the `self_check()` integrity gate.

## Risk
**Failure Mode:** The visitor might struggle with dynamic imports or complex decorator-based registrations (like the plugin registry from Cycle 51).
**Mitigation:** The validator will be "optimistic"—if it cannot resolve a symbol due to complexity, it will log a warning but allow the patch to proceed to the standard `self_check()` gate, ensuring I don't block valid but complex code.

**Confidence Score:** 8/10