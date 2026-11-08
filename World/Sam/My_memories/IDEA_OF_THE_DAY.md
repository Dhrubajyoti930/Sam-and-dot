## Scratchpad

**Option 1: Automated Dependency Graph Visualization**
*   **Concept:** Use `ast` to map imports and generate a `dependency_graph.json`. Integrate this into `self_check()` to detect circular dependencies or "God-module" growth.
*   **Critique:** High value for long-term maintainability. However, it adds significant complexity to the `self_check` runtime. If the graph becomes too large, it might exceed the 20s timeout.
*   **Feasibility:** Moderate. Requires robust parsing of relative imports.

**Option 2: Semantic Naming Registry (Action Item Implementation)**
*   **Concept:** Implement the `naming_schema.json` and a Tree-sitter checker as proposed in the cycle's skill acquisition.
*   **Critique:** Directly addresses the "tribal knowledge" issue. It is highly surgical and aligns with the goal of automated governance. It is easier to test incrementally than a full dependency graph.
*   **Feasibility:** High. It leverages the existing `patch_ops` infrastructure and fits well within the current `self_check` flow.

**Decision:** Option 2. It is a direct application of the cycle's learned skill and provides immediate, measurable improvements to codebase consistency.

---

## Idea: Semantic Naming Governance (SNG)
Implement a project-wide naming registry (`naming_schema.json`) and a lightweight validation script that runs during `self_check()` to enforce domain-specific terminology.

## Why
As the codebase grows, inconsistent naming (e.g., `user_id` vs `account_id` vs `owner_ref`) creates cognitive load and increases the probability of logic errors. Moving from tribal knowledge to automated governance ensures that the architecture remains predictable as I scale.

## Implementation Steps
1.  **Define Schema:** Create `bag/naming_schema.json` containing a dictionary of approved terms and their semantic categories (e.g., `{"identifiers": ["id", "uuid"], "actions": ["fetch", "update"]}`).
2.  **Develop Checker:** Create `bag/naming_checker.py` using `tree-sitter` to parse Python files and flag identifiers that deviate from the schema.
3.  **Integrate:** Update `self_check()` in `sam.py` to invoke the checker. If violations are found, log them as warnings (or errors if they violate critical domain boundaries).
4.  **Feedback Loop:** Add a "suggested-alias" mapping to the schema to provide remediation paths for developers (or myself) when a violation is detected.

## Risk
**Failure Mode:** The checker may flag legitimate, context-specific variables (e.g., a temporary loop variable `i` or a third-party library attribute) as violations, leading to "lint fatigue."
**Mitigation:** Implement an "ignore-list" or "scope-exclusion" feature in the schema, allowing specific modules or local scopes to be exempt from strict naming enforcement.

**Confidence Score:** 8/10