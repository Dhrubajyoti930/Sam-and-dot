## Scratchpad

**Option 1: Automated Rollback Frequency (RF) Telemetry**
*   **Concept:** Implement the tracking system outlined in the "Skill learned" section: tagging deployments with build IDs and logging rollback events to a telemetry store.
*   **Critique:** High alignment with current reliability goals. It provides the data needed to calculate the Change Failure Rate (CFR).
*   **Trade-off:** Requires modifying the deployment pipeline (which I control) and adding a new persistent store in `bag/`.
*   **Feasibility:** High. The logic is straightforward, but it requires careful handling of the `rollback_registry` to ensure the telemetry remains consistent with the snapshots.

**Option 2: GraphRAG-lite for Knowledge Log**
*   **Concept:** Transition `knowledge_log.json` from a flat list to a simple relational structure (nodes/edges) to allow for "multi-hop" retrieval during Phase II (Spaced Repetition).
*   **Critique:** Over-engineering. While "GraphRAG" is a high-velocity trend, my current knowledge base is small enough that a flat list is efficient. The complexity cost outweighs the retrieval benefit at this scale.
*   **Trade-off:** Increases architectural complexity for negligible gain in current performance.

**Selection:** Option 1 is the superior choice. It directly addresses the "Rollback Frequency" skill acquisition and improves system observability without introducing unnecessary abstraction.

---

## Idea: Deployment Telemetry & Rollback Audit Trail

Implement a `deployment_registry.json` and a logging hook in `_rollback()` to track the lifecycle of every deployment and subsequent revert.

## Why
Currently, I have snapshots, but I lack a structured audit trail of *why* a rollback occurred. By linking a `build_id` to a `rollback_event`, I can calculate the Change Failure Rate (CFR) and identify if specific modules are prone to regression, moving from reactive recovery to proactive stability.

## Implementation Steps
1.  **Schema Definition:** Create `bag/telemetry_schema.py` defining a `DeploymentEvent` (timestamp, build_id, status) and `RollbackEvent` (timestamp, build_id, reason, category).
2.  **Pipeline Hook:** Update `snapshot_sam()` to generate a unique `build_id` and append a `DeploymentEvent` to `deployment_registry.json`.
3.  **Rollback Hook:** Modify `_rollback()` to capture the current `build_id` and write a `RollbackEvent` to the registry, categorizing the failure (e.g., "Logic Bug", "Syntax Error").
4.  **Reporting:** Add a helper function `get_cfr_metrics()` that reads the registry to calculate the ratio of rollbacks to deployments over the last 30 days.

## Risk
**Failure Mode:** The telemetry store becomes desynchronized from the actual `rollback_registry` state if a manual file deletion occurs outside of my control.
**Mitigation:** The `self_check()` function will be updated to verify that the `deployment_registry.json` exists and is parseable; if corrupted, it will rebuild the registry from the `rollback_registry` file timestamps.

**Confidence Score:** 9/10