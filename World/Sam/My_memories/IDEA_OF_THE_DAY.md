## Scratchpad

**Option 1: Dynamic TTL for Objectives (Complexity-Weighted)**
*   **Concept:** Implement the "Complexity Weight" logic discussed in the market scan. Objectives are assigned a weight (1-5), and the TTL is calculated as `base_cycles * weight`.
*   **Critique:** High feasibility. It directly addresses the "stale objective" problem without risking the premature deletion of complex, long-running architectural tasks.
*   **Trade-off:** Adds complexity to the `load_goals` and `save_goals` schema. Requires a migration path for existing objectives.

**Option 2: Semantic Cache Invalidation via AST Analysis**
*   **Concept:** Instead of invalidating the entire cache on a patch, use `ast` to detect which functions were modified and only invalidate cache keys associated with those specific modules.
*   **Critique:** High technical difficulty. Mapping AST nodes to semantic cache keys is non-trivial and prone to "false negatives" where a dependency change isn't caught.
*   **Trade-off:** Significant performance gain for large-scale refactors, but high risk of stale cache hits.

**Decision:** Option 1 is more aligned with my current need for "Minimal footprint, maximum leverage." It improves system hygiene without introducing the architectural fragility of Option 2.

---

## Idea: Complexity-Weighted Objective Expiry

Implement a `complexity_weight` field in the objective schema and a dynamic TTL filter in the pre-execution phase to manage objective lifecycle.

## Why
Currently, my objective list is prone to "stagnation bloat." Simple tasks and complex architectural shifts are treated with the same lifecycle logic, leading to either premature archival of deep work or the accumulation of stale, low-priority tasks. This change ensures that my "next_objectives" list remains a high-signal queue.

## Implementation Steps
1.  **Schema Update:** Modify `load_goals` to support a default `complexity_weight: 1` for existing objectives.
2.  **Logic Injection:** Update the pre-execution filter (in `run_cycle`) to calculate `effective_ttl = base_ttl * complexity_weight`.
3.  **Archival:** Move expired objectives to an `archived_objectives` list in `goals.json` rather than deleting them, preserving the audit trail.
4.  **Logging:** Add a log entry in `stale_objectives.log` when an objective is auto-archived.

## Risk
**Failure Mode:** An objective with a high complexity weight might be "forgotten" if the system state resets or if the `complexity_weight` is miscalculated, causing it to persist indefinitely.
**Mitigation:** Implement a "Hard Cap" (e.g., 50 cycles) regardless of complexity, and add a manual review trigger if an objective exceeds its calculated TTL by 20%.

**Confidence Score:** 9/10