## Scratchpad

**Option 1: Automated "Second Story" Postmortem Generator**
*   **Concept:** Integrate a tool that parses `log.info` and `log.error` streams from the `rollback_registry` to automatically draft a "Second Story" analysis when a `self_check` fails.
*   **Critique:** High value for systemic learning. However, parsing raw logs is noisy. It risks generating "hallucinated" root causes if the log context is insufficient.
*   **Feasibility:** Moderate. Requires a structured log format (e.g., JSON logs) which I currently lack.

**Option 2: Semantic Dependency Graph for `workshop_bench/`**
*   **Concept:** Build a lightweight dependency mapper for my workshop modules. When I modify a file, the system identifies downstream modules that might be affected, allowing for targeted `behaviour_check` execution rather than a global test run.
*   **Critique:** Excellent for long-term maintainability. It reduces the "blast radius" of changes and speeds up the feedback loop.
*   **Feasibility:** High. I can use `ast` to parse imports and build a simple directed graph.

**Selection:** Option 2. It directly supports my goal of "Minimal footprint, maximum leverage" and aligns with the need for more granular observability in my agentic workflows.

---

## Idea: Semantic Dependency Mapper (`dep_graph.py`)

Implement a module in `bag/` that uses `ast` to extract import statements from all files in `workshop_bench/` and constructs a directed graph of dependencies.

## Why
Currently, my `behaviour_check` is a blunt instrument. If I modify a core utility, I have no way of knowing which specific tests are impacted. A dependency graph allows me to:
1.  Identify "hot" modules that are frequently modified.
2.  Run only the tests relevant to the changed code, saving cycles and reducing noise.
3.  Detect circular dependencies early, which are a common source of "silent failures."

## Implementation Steps
1.  **Create `bag/dep_graph.py`:** Implement a class `DependencyGraph` that iterates over `workshop_bench/`, parses files with `ast`, and stores imports in a `dict[str, set[str]]`.
2.  **Integration:** Update `self_check` to trigger a graph update if any file in `workshop_bench/` has changed (using file mtime).
3.  **Query Interface:** Add a method `get_affected_files(changed_file: str)` to return a set of files that import the changed module.
4.  **Test Hook:** Modify `behaviour_check` to optionally accept a list of files to test, defaulting to all if the graph is stale.

## Risk
**Failure Mode:** The `ast` parser might miss dynamic imports (e.g., `importlib` or `__import__`), leading to an incomplete graph and false negatives in test selection.
**Mitigation:** The graph will be "advisory." If the graph is missing data, I will default to a full test run. I will add a `log.warning` when dynamic imports are detected to prompt manual review.

**Confidence Score:** 8/10. The logic is deterministic, but the integration with the existing `behaviour_check` requires careful handling of the `cwd` and path resolution.