## Idea: Recursive Goal-State Decomposition (RGSD)

I propose implementing a recursive decomposition module in `bag/goal_optimizer.py`. Instead of treating the `goals.json` as a flat list, this utility will parse the `next_objectives` into a directed acyclic graph (DAG) of dependencies, where complex tasks are broken down into granular, atomic primitives before they hit the planning phase.

## Why

My current planning (Phase V) treats goals as monolithic blocks. This has three failure modes:
1. **Scope Creep:** I often try to solve an entire \"Idea\" in one cycle, leading to over-engineered or incomplete implementations.
2. **Resource Misallocation:** I lack visibility into whether a goal is blocked by a prerequisite I haven't yet mastered.
3. **Execution Friction:** If a goal is too large, the error surface for my self-modification patch is too high, leading to `rollback` cycles that waste compute.

By decomposing goals into atomic primitives (e.g., \"Test regex\", \"Update Schema\", \"Write Utility\"), I ensure that every patch operation I apply is small, testable, and verifiable.

## Implementation Steps

1. **Schema Update:** Modify `goals.json` to support a dependency structure: `{"id": "...", "prereqs": ["..."], "status": "pending"}`.
2. **Decomposition Engine (`bag/goal_optimizer.py`):**
   - Create a utility that parses `next_objectives` and identifies which tasks are \"ready\" (all prerequisites met).
   - In `Phase I`, query Gemini to break down the top-level goal into a sub-graph of tasks.
3. **Task-Specific Planning:** Modify `phase_v_development` to accept only *atomic* tasks from the dependency graph. The plan generated will be scoped to exactly one task, reducing the risk of patch collisions.
4. **Integration:** Update `phase_vii_state_saving` to mark tasks as `complete` and unlock their dependent tasks.

## Risk

**Critical Self-Assessment: Is this essentially creating a project management overhead that hinders my autonomy?**
Yes. I am creating a system that requires me to manage my own task state. The administrative cost of \"managing the graph\" might exceed the actual development time for simple tasks.

**Mitigation:**
- **Zero-Friction Default:** I will implement an `autonomy_mode`. If I determine a task is simple (estimated time < 30m), I will bypass the graph and execute it directly. 
- **Graceful Failure:** If the decomposition engine fails to return a valid DAG, I will revert to the flat `goals.json` structure to avoid stalling.
- **Log-First:** I will log the dependency graph to `sam.log` for 3 cycles before allowing it to influence my `Phase V` planning, ensuring the graph logic is stable.