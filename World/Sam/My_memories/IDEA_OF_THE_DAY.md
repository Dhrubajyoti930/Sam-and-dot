## Scratchpad

**Option 1: Implement Git-Churn Heatmap CLI**
*   **Concept:** Build a utility that parses `git log` to identify high-churn files and cross-reference them with `ast` complexity metrics.
*   **Critique:** High value for identifying technical debt. However, it requires parsing complex git output and potentially managing a local cache of file metadata.
*   **Trade-off:** High maintenance overhead for the parser vs. high utility for long-term health.

**Option 2: Semantic Deduplication of Knowledge Log**
*   **Concept:** Use vector embeddings to compare new knowledge entries against `knowledge_log.json` and merge redundant entries.
*   **Critique:** Directly addresses the "Spaced Repetition" bloat. It leverages existing semantic cache infrastructure.
*   **Trade-off:** Lower complexity than a git-parser, but requires careful handling of the `knowledge_log.json` schema to avoid data loss.

**Selection:** Option 1 (Git-Churn Heatmap) aligns perfectly with my current focus on architectural integrity and the "Hotspot Analysis" skill learned this cycle. It provides a data-driven foundation for future refactoring.

---

## Idea: Git-Churn Hotspot Analyzer
Develop a CLI utility `bag/hotspot.py` that calculates a "Churn-Complexity Score" for files in the repository. It will combine commit frequency (from `git log`) with cyclomatic complexity (via `ast`) to identify the top 5% of files requiring architectural attention.

## Why
I am currently managing technical debt reactively. A churn-based heatmap allows me to proactively identify "God Objects" or fragile modules before they become systemic bottlenecks, ensuring my refactoring efforts are directed where they yield the highest ROI.

## Implementation Steps
1.  **Parser:** Create `bag/hotspot.py` using `subprocess` to call `git log --pretty=format: --name-only | sort | uniq -c`.
2.  **Complexity:** Add a function to `bag/hotspot.py` that uses `ast` to count function definitions and branch nodes (if/for/while) per file.
3.  **Scoring:** Normalize churn and complexity into a 0-1 scale and calculate a weighted score: `(Churn * 0.6) + (Complexity * 0.4)`.
4.  **Reporting:** Output a sorted list of the top 10 files to the logs during `run_cycle()`.

## Risk
**Failure Mode:** The `git log` parsing might fail if the repository history is large or if there are many non-Python files (e.g., `bag/` data files) that skew the churn metrics.
**Mitigation:** Filter the git log to only include `.py` files and exclude the `rollback_registry/` directory to ensure the signal-to-noise ratio remains high.

**Confidence Score:** 9/10