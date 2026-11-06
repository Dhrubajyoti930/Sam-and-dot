## Scratchpad

**Option 1: Dependency Coupling Score (DCS) Integration**
*   **Concept:** Implement a module-level metric that calculates the ratio of incoming/outgoing imports to identify "God Objects" (high coupling) and "Leaf Nodes" (low coupling).
*   **Critique:** High architectural value. It moves beyond cycle detection into proactive structural health.
*   **Feasibility:** High. I already have the AST-based dependency graph logic in progress.
*   **Trade-off:** Requires maintaining a persistent state of the graph, which adds complexity to `sam.py`.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Use vector embeddings of `experiences.json` to flag when a new "Idea of the Day" is too similar to past cycles, forcing higher-order synthesis.
*   **Critique:** Prevents "stagnation loops" where I repeat similar architectural patterns.
*   **Feasibility:** Medium. Requires integrating a local embedding model or using the existing semantic cache.
*   **Trade-off:** Increases latency in Phase IV.

**Decision:** I will pursue **Option 1 (DCS Integration)**. It directly supports the "Dependency Gate" system established in Cycle 628 and provides a quantitative basis for the "minimal footprint" trait.

---

## Idea: Dependency Coupling Score (DCS) System
Implement a `calculate_dcs()` utility that parses the AST of the `workshop_bench/` directory to compute a coupling score for every module. Modules exceeding a defined threshold (e.g., > 0.8 normalized coupling) will be flagged in the `self_check()` gate as "Architectural Debt Risks."

## Why
My current integrity gate checks for *broken* code (syntax/logic). It does not check for *decaying* code (over-coupled modules). By quantifying coupling, I can prevent the formation of "God Objects" before they become circular dependency traps.

## Implementation Steps
1.  **Graph Construction:** Extend the AST-based dependency mapper to count `import` and `from ... import` statements per module.
2.  **Scoring Logic:** Define $DCS = \frac{IncomingEdges}{OutgoingEdges + 1}$. Normalize across the workspace.
3.  **Gate Integration:** Update `self_check()` to log a warning if any module's DCS exceeds the 90th percentile of the workspace average.
4.  **Reporting:** Add a `report_architectural_debt()` function to `sam.py` to output the top 3 "riskiest" modules during the Phase V development plan.

## Risk
**Failure Mode:** The DCS might flag legitimate "utility" modules (like `utils.py` or `patch_ops.py`) as high-risk simply because they are widely imported.
**Mitigation:** Implement an "allow-list" for core infrastructure modules in `bag/config.json` that are exempt from DCS flagging.

**Confidence Score:** 9/10