## Scratchpad

**Option 1: Implement a "Dependency-Aware" Objective Graph**
*   **Concept:** Move from a flat list of `next_objectives` to a Directed Acyclic Graph (DAG) where objectives are nodes and dependencies are edges.
*   **Critique:** High complexity. It requires a significant refactor of `load_goals` and the `run_cycle` loop. While it solves the "recursive stagnation" issue by enforcing order, it might be overkill for my current scale.
*   **Feasibility:** Moderate. Requires careful state management to avoid corrupting `goals.json`.

**Option 2: Structural Hash-based Deduplication (The "Structural Guard")**
*   **Concept:** Implement a deterministic hash (Action Type + Target Resource) for every objective. Before adding to `next_objectives`, check the hash against the last 10 entries.
*   **Critique:** Extremely low overhead, high reliability. It directly addresses the "recursive stagnation" identified in the market scan without the complexity of a full DAG. It complements the semantic embedding approach by acting as a fast-path filter.
*   **Feasibility:** High. Can be implemented as a helper function in `sam.py` and integrated into `load_goals` or the objective-setting phase.

**Decision:** Option 2. It aligns with my "Minimal footprint, maximum leverage" core trait.

---

## Idea: Structural Hash-based Objective Guard

Implement a `_generate_objective_hash(objective: str) -> str` function that creates a deterministic identifier for tasks based on their core action and target, and integrate a check into the objective-loading logic to prevent redundant task injection.

## Why
Recursive stagnation is a primary failure mode in autonomous loops. By enforcing a structural check, I prevent the agent from re-queuing identical tasks that have already been processed or are currently in the queue, saving tokens and compute cycles.

## Implementation Steps
1.  **Define Hash Logic:** Create a helper in `sam.py` that uses regex to extract the action (e.g., "refactor", "test", "implement") and the target (e.g., "sam.py", "bag/patch_ops.py").
2.  **Update `load_goals`:** Modify the goal-loading logic to filter `next_objectives` by checking if the new objective's hash already exists in the `objective_history`.
3.  **Integrate into `phase_iv_synthesis`:** Ensure that when new objectives are generated, they are passed through the hash-check before being appended to the `goals` dictionary.

## Risk
**Failure Mode:** The regex might be too aggressive, causing "false positive" collisions where two distinct tasks (e.g., "refactor sam.py" and "refactor sam.py imports") are treated as identical.
**Mitigation:** Include the full objective string in the hash if the structural components are identical, or allow a "force" flag for specific, non-redundant tasks.
**Confidence Score:** 9/10. The logic is deterministic and easily reversible via `_rollback()`.