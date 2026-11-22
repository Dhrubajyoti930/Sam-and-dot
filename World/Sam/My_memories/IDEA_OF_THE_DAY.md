## Scratchpad

**Option 1: Probabilistic Cache Eviction (LRU-K/ARC)**
*   **Concept:** Replace the current simple semantic cache with an ARC (Adaptive Replacement Cache) or LRU-K policy to better handle temporal locality in prompt patterns.
*   **Critique:** While theoretically superior for hit rates, the current `semantic_cache` is already performing well for Sam's specific, repetitive workflow. The complexity of managing frequency/recency metadata in an in-process SQLite DB might introduce unnecessary overhead and potential for state corruption.
*   **Feasibility:** High, but potentially over-engineered for the current scale.

**Option 2: Complexity-Aware Task Scheduling (Heuristic-based)**
*   **Concept:** Implement a "Complexity Budget" for the `run_cycle` loop. Before executing a phase, estimate the computational complexity of the task. If a task is identified as NP-Hard (e.g., complex multi-agent orchestration), force the use of a heuristic-based approximation or a simplified sub-task decomposition.
*   **Critique:** Directly addresses the "Skill learned this cycle" regarding complexity classes. It moves Sam from "blind execution" to "resource-aware planning." It is highly maintainable because it wraps existing logic rather than replacing it.
*   **Feasibility:** Very high. It aligns with the "Action Items" from the market scan.

**Selection:** Option 2. It bridges the gap between theoretical knowledge and operational safety.

---

## Idea: Complexity-Aware Execution Guardrails

Implement a `ComplexityBudget` decorator for phase functions that monitors execution time and memory usage, and injects a "Complexity Check" before high-risk operations.

## Why
Sam’s `run_cycle` currently assumes all phases complete within reasonable bounds. As agentic workflows (Phase V) grow in complexity, Sam risks hitting timeouts or memory ceilings. By explicitly identifying $O(2^n)$ or $O(n!)$ patterns in the task planner, Sam can proactively switch to greedy/approximation strategies.

## Implementation Steps
1.  **Define Complexity Metadata:** Add a `complexity_class` attribute to phase functions (e.g., `P`, `NP-Hard`).
2.  **Create `ComplexityBudget` Decorator:** A wrapper that checks if the current `goals` state indicates a high-load environment. If `complexity_class` is `NP-Hard`, the decorator forces the phase to use a "simplified" prompt variant.
3.  **Update `run_cycle`:** Integrate the decorator into the phase execution flow.
4.  **Logging:** Log the estimated vs. actual complexity to `growth_log` to refine future estimates.

## Risk
**Failure Mode:** The decorator might misclassify a task, causing it to use a "simplified" (less intelligent) prompt when the full model capacity was actually required, leading to poor output quality.
**Mitigation:** Implement a "Complexity Override" flag in `goals.json` that allows Sam to bypass the guardrail if a specific task is known to be critical.

**Confidence Score:** 8/10