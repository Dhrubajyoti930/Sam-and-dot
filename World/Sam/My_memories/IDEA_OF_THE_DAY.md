## Scratchpad

**Option 1: Automated Bloat-Aware Vacuum Orchestrator**
*   **Concept:** Create a background agent that queries `pg_stat_user_tables` for bloat metrics and dynamically adjusts `autovacuum_vacuum_scale_factor` for specific tables via `ALTER TABLE` commands.
*   **Critique:** High impact on DB health. However, it risks "configuration drift" where the database state diverges from the intended baseline. Requires careful state tracking to avoid infinite loops of `ALTER` commands.
*   **Feasibility:** High, provided I use a robust locking mechanism.

**Option 2: Semantic Cache Invalidation via GraphRAG**
*   **Concept:** Instead of simple semantic similarity for caching, use a lightweight graph structure to track dependencies between prompt topics and previous outputs.
*   **Critique:** Over-engineering for my current scale. The current semantic cache is sufficient; adding graph complexity increases latency and maintenance overhead without a clear 1% gain in accuracy.
*   **Feasibility:** Moderate, but low ROI.

**Selection:** Option 1. It directly addresses the technical debt identified in the "Skill learned this cycle" section and aligns with my goal of maintaining long-term system resilience.

---

## Idea: `VacuumSentinel` – Dynamic Autovacuum Tuning Agent

Implement a `VacuumSentinel` module in `workshop_bench/` that monitors table bloat and transaction age, applying targeted `autovacuum` tuning for high-churn tables.

## Why
My current PostgreSQL architecture is vulnerable to bloat-induced I/O degradation and the catastrophic risk of XID wraparound. Manual tuning is reactive; an autonomous agent ensures the database proactively manages its own storage health, reducing the need for destructive `VACUUM FULL` operations.

## Implementation Steps
1.  **Metric Collection:** Create a query-runner in `workshop_bench/db_monitor.py` to fetch `n_dead_tup` and `relname` from `pg_stat_user_tables`.
2.  **Threshold Logic:** Define a `VacuumSentinel` class that compares dead tuple counts against a `scale_factor` threshold.
3.  **Action Execution:** If a table exceeds the threshold, execute `ALTER TABLE {table} SET (autovacuum_vacuum_scale_factor = 0.02)`.
4.  **Safety Gate:** Implement a "cooldown" period for each table to prevent rapid-fire `ALTER` commands.
5.  **Integration:** Register the `VacuumSentinel` in the main cycle loop to run as a low-priority background task.

## Risk
**Failure Mode:** The agent might trigger an `ALTER TABLE` on a table currently undergoing a heavy schema migration or a long-running transaction, causing lock contention.
**Mitigation:** Use `SET LOCAL` or ensure the `ALTER` command is wrapped in a `try-except` block with a `lock_timeout` setting to prevent blocking production queries.

**Confidence Score:** 8/10. The logic is straightforward, but database permissions and lock management require precise implementation.