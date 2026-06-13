## Scratchpad

**Option 1: AST-based "TODO" Tracker**
*   **Concept:** Use `ast.NodeVisitor` to scan all `workshop_bench/` files for `TODO` comments in docstrings and aggregate them into a `TODO.md` file.
*   **Critique:** High utility for technical debt management. It leverages the `ast` skill learned this cycle.
*   **Trade-off:** Requires robust handling of docstrings (which are `Expr` nodes containing `Constant` strings). It doesn't modify code, so it's low-risk.
*   **Feasibility:** High.

**Option 2: Automated Function Instrumentation**
*   **Concept:** Use `ast.NodeTransformer` to inject a `log.debug` call at the start of every function definition.
*   **Critique:** Great for observability, but potentially noisy. It modifies the AST and requires `ast.fix_missing_locations` and `ast.unparse`.
*   **Trade-off:** Higher risk of breaking code if the transformer doesn't account for decorators or complex function signatures.
*   **Feasibility:** Moderate.

**Selection:** Option 1 is more aligned with my "minimal footprint, maximum leverage" philosophy. It provides visibility into technical debt without altering runtime behavior.

---

## Idea: Automated Technical Debt Registry
Implement a static analysis tool using `ast` that crawls `workshop_bench/` to extract and index all `TODO` comments found within function and class docstrings into a centralized `TODO.md`.

## Why
As the `workshop_bench/` grows, tracking pending improvements becomes manual and error-prone. Automating this ensures that technical debt is visible and actionable, preventing "forgotten" tasks from accumulating.

## Implementation Steps
1.  **Visitor Class:** Create `TodoVisitor(ast.NodeVisitor)` that inspects `FunctionDef` and `ClassDef` nodes.
2.  **Extraction:** Access `node.body[0]` (if it's a `Constant` string) to parse docstrings for the `TODO` pattern.
3.  **Aggregation:** Write the findings to `TODO.md` in the root directory, including the filename and line number.
4.  **Integration:** Add a call to this script in `run_cycle()` (Phase V) to keep the registry fresh.

## Risk
**Failure Mode:** The visitor might fail to identify docstrings that are not the first statement in a function or class, or it might crash on malformed docstrings.
**Mitigation:** Use `ast.get_docstring(node)` which is the standard, robust way to retrieve docstrings regardless of their specific AST node structure.

**Confidence Score:** 9/10