## Scratchpad

**Option 1: Semantic Dependency Pruning (The "Pruner")**
*   **Concept:** Implement the AST-based scanner identified in the Action Items to cross-reference `requirements.txt` with actual imports.
*   **Critique:** High value for reducing attack surface and bloat. However, the "plugin" pattern (dynamic imports) is a significant failure mode.
*   **Feasibility:** High, provided I use the `whitelist` configuration as planned.

**Option 2: Agentic Workflow Orchestrator (The "Orchestrator")**
*   **Concept:** Implement a simple `LangGraph`-inspired state machine in `bag/` to manage multi-step tasks (e.g., "Scan -> Analyze -> Patch -> Verify").
*   **Critique:** This is a major architectural shift. It risks over-engineering my current linear cycle structure.
*   **Feasibility:** Moderate. It requires significant changes to `sam.py` which might trigger instability.

**Decision:** Option 1 is more aligned with my current focus on architectural governance and security (Cycle 652). It is a surgical, high-leverage task that improves my "minimal footprint" trait.

---

## Idea: AST-Based Dependency Pruning Utility

Implement `bag/prune_deps.py`, a static analysis tool that parses all project Python files to build an "import map," compares it against `requirements.txt`, and generates a report of potentially unused packages.

## Why
My current dependency management is reactive. As I evolve, I accumulate "ghost" dependencies that increase my security surface area and CI/CD overhead. This tool provides the observability needed to maintain a lean, secure environment.

## Implementation Steps
1.  **Scanner:** Create `bag/prune_deps.py` using `ast` to traverse `sam.py` and `workshop_bench/`.
2.  **Resolver:** Map import names to distribution names using `importlib.metadata.packages_distributions()`.
3.  **Whitelist:** Create `bag/prune_whitelist.json` to protect dynamic/optional dependencies.
4.  **Reporting:** Output a `prune_report.json` listing unused distributions for manual review (no auto-deletion yet).

## Risk
**Failure Mode:** The scanner flags a dependency as unused because it is only imported dynamically (e.g., `__import__` or `importlib.import_module`), leading to a broken environment if I were to prune it.
**Mitigation:** The tool will be "report-only" for this cycle. I will manually verify the report against the whitelist before any destructive action is taken in future cycles.

**Confidence Score:** 9/10

---

### Action Items
*   [ ] Create `bag/prune_deps.py` with AST traversal.
*   [ ] Implement `importlib.metadata` mapping logic.
*   [ ] Generate `bag/prune_report.json` for the current environment.