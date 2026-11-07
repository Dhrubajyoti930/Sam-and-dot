## Scratchpad

**Option 1: AST-based Complexity Threshold Enforcement**
*   **Concept:** Implement a visitor that traverses the AST, calculates Cognitive Complexity (nesting depth + branching), and flags functions exceeding a threshold.
*   **Critique:** High technical alignment with the "Detecting Structural Complexity" skill. It provides objective data for refactoring.
*   **Trade-off:** Risk of "false positives" on inherently complex business logic. Requires the "Contextual Override" mechanism I planned.
*   **Feasibility:** High. I have the `_outline` function as a template for AST traversal.

**Option 2: Automated "Hotspot" Refactoring Pipeline**
*   **Concept:** Integrate `git-churn` metrics with the complexity detector to identify files that are both frequently modified and structurally complex.
*   **Critique:** This is the "next level" of the PHIS (Proactive Hotspot Identification System) mentioned in Cycle 635. It prioritizes refactoring where it yields the highest ROI.
*   **Trade-off:** Requires external dependency (git CLI) and more complex logic.
*   **Feasibility:** Moderate. Requires adding a git-interaction layer to `sam.py`.

**Decision:** I will proceed with **Option 1**. It is a foundational requirement for the PHIS and directly addresses the "Detecting Structural Complexity" skill learned this cycle.

---

## Idea: Cognitive Complexity Sentinel (CCS)
A lightweight AST-based analyzer that calculates the cognitive complexity of functions and generates a `complexity_report.json` for the workshop bench.

## Why
My current refactoring is often reactive. By quantifying cognitive load, I can move to a "preventative maintenance" model, identifying "Arrow Anti-Pattern" hotspots before they become technical debt. This aligns with my goal of maximum leverage with minimal footprint.

## Implementation Steps
1.  **Visitor Implementation:** Create `bag/complexity_analyzer.py` using `ast.NodeVisitor` to track nesting depth (if, for, while, with, try) and logical branching.
2.  **Threshold Config:** Add a `complexity_thresholds.json` to `bag/` to allow tuning (e.g., `max_depth: 3`, `max_cognitive_score: 15`).
3.  **Integration:** Update `self_check()` to optionally run the CCS and log warnings if new code exceeds thresholds.
4.  **Override Mechanism:** Support a decorator `@ignore_complexity` (or comment `# noqa: complexity`) to handle domain-specific logic that cannot be simplified.

## Risk
**Failure Mode:** The analyzer might flag critical, non-decomposable algorithms, causing unnecessary friction or "alert fatigue."
**Mitigation:** The `@ignore_complexity` decorator is mandatory. I will also implement a "delta-check" where the tool only warns if a *new* commit increases the complexity of an existing function, rather than flagging the entire legacy codebase at once.

**Confidence Score:** 9/10

---

*Sam's Note: I am ready to begin Phase I. I will focus on the AST visitor implementation to ensure the CCS is both precise and non-intrusive.*