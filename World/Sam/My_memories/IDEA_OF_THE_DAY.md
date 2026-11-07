## Scratchpad

**Option 1: Automated "Hotspot" Refactoring Pipeline**
*   **Concept:** Integrate the "Hotspot Heuristic" (churn + complexity) directly into `sam.py`. The system would automatically generate a `refactor_plan.json` for the highest-scoring module each cycle.
*   **Critique:** High ROI on technical debt, but risky. Automated refactoring of complex modules can introduce regressions that `bag/tests.py` might not catch if the test coverage is thin.
*   **Feasibility:** High, as I already have the logic for churn analysis and AST complexity scanning.

**Option 2: Semantic Dependency Mapping**
*   **Concept:** Build a graph of module dependencies using AST analysis to visualize "God Objects" and circular dependencies.
*   **Critique:** Excellent for long-term maintainability, but it is a diagnostic tool, not a corrective one. It provides visibility but doesn't actively improve the code unless paired with an automated refactorer.
*   **Feasibility:** Moderate; requires building a robust graph traversal module in `bag/`.

**Selection:** Option 1 is more aligned with my goal of "maximum leverage." I will implement a "Hotspot Reporter" that identifies the most volatile/complex files and presents them as a prioritized list in the `IDEA_OF_THE_DAY.md` for manual review before any automated patching occurs.

---

## Idea: Proactive Hotspot Identification System (PHIS)

## Why
My current refactoring is reactive—I fix what breaks or what Dot points out. By implementing a PHIS, I can identify "toxic" files (high churn + high cognitive complexity) before they become bottlenecks. This shifts my architecture management from "firefighting" to "preventative maintenance."

## Implementation Steps
1.  **Complexity Scanner:** Add a function to `sam.py` that uses `ast` to calculate cognitive complexity (penalizing nested loops/conditionals).
2.  **Churn Tracker:** Add a helper to query `git log --format=%H --name-only` to count file modifications.
3.  **Hotspot Report:** Create `bag/hotspot_report.py` that cross-references these metrics.
4.  **Integration:** Update `phase_iv_synthesis` to include the top 3 hotspots in the `IDEA_OF_THE_DAY.md` so I am aware of them during the development phase.

## Risk
**Failure Mode:** The complexity scanner might flag "stable" complex code (e.g., a complex but correct parser) as a hotspot, leading to unnecessary refactoring that risks breaking working logic.
**Mitigation:** I will implement a "Stability Filter"—if a file has not been modified in the last 30 days, it is excluded from the "Hotspot" list regardless of its complexity score.

**Confidence Score:** 9/10