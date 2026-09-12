## Scratchpad

**Option 1: PostgreSQL Window Function Refactor (Analytics Module)**
*   **Concept:** Replace existing self-joins in the analytics module with `LAG()` and `LEAD()` window functions to calculate deltas.
*   **Critique:** High performance gain for time-series analysis. However, it requires modifying existing SQL queries which are currently stable.
*   **Trade-off:** Better execution plans vs. risk of breaking existing reporting logic.
*   **Feasibility:** High. The logic is well-understood and fits the "Action Items" identified in the skill-learning phase.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a script to identify and merge redundant logs in `bag/` using semantic similarity (embeddings) rather than exact string matching.
*   **Critique:** This addresses a long-term maintainability issue (log bloat). It is more complex than Option 1 but provides higher long-term leverage.
*   **Trade-off:** Increased complexity (requires embedding generation) vs. cleaner state management.
*   **Feasibility:** Moderate. Requires integrating a lightweight embedding model or API call.

**Decision:** I will proceed with **Option 1**. It is a high-leverage, low-risk refactor that directly applies the skill learned this cycle and satisfies the "Action Items" list.

---

## Idea: PostgreSQL Window Function Migration
Refactor the `analytics_engine.py` (or equivalent module) to replace self-join delta calculations with `LAG()` window functions.

## Why
Current self-joins create a Cartesian product overhead, which scales poorly as the `bag/` logs grow. `LAG()` allows for single-pass calculation of deltas (e.g., `current_value - previous_value`), significantly reducing memory pressure and CPU cycles during analytical aggregation.

## Implementation Steps
1.  **Identify Targets:** Locate all SQL queries in the analytics module using `JOIN` on the same table for delta calculations.
2.  **Draft Query:** Rewrite queries using `LAG(column_name) OVER (PARTITION BY entity_id ORDER BY timestamp ASC)`.
3.  **Index Verification:** Ensure the `PARTITION BY` and `ORDER BY` columns are covered by a composite index to prevent memory spills.
4.  **Validation:** Run existing tests in `bag/tests.py` to ensure output parity between the old self-join and the new window function.

## Risk
**Failure Mode:** The `ORDER BY` clause in the window function might produce different results if the `timestamp` column contains non-unique values, leading to non-deterministic delta calculations.
**Mitigation:** Include a unique identifier (e.g., `id` or `created_at` + `sequence_id`) in the `ORDER BY` clause to ensure a stable sort order.

**Confidence Score:** 9/10