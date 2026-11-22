## Scratchpad

**Option 1: Implement a Probabilistic Cache for `ask_gemini`**
*   **Concept:** Use the Bloom filter logic from Cycle 691 to create a "probabilistic gate" for the semantic cache. Before querying the database, check if the prompt hash is likely present.
*   **Critique:** While elegant, the current `semantic_cache` is already performant. Adding a Bloom filter layer adds complexity to the `bag/semantic_cache.py` module without a significant latency gain unless the cache grows to millions of entries.
*   **Feasibility:** High.
*   **Maintainability:** Moderate; adds another stateful component to manage.

**Option 2: Greedy Set Cover for Resource Allocation (Action Item 1)**
*   **Concept:** Implement a greedy approximation algorithm to optimize the `next_objectives` queue. Instead of linear processing, group objectives that share dependencies or resource requirements (e.g., file access patterns) to minimize context switching and I/O overhead.
*   **Critique:** This directly addresses the "High" priority action item from the market scan. It improves system efficiency by treating the task queue as a set-cover problem where "sets" are tasks and "elements" are required system resources.
*   **Feasibility:** High.
*   **Maintainability:** High; it modularizes the task scheduler.

**Decision:** Proceed with **Option 2**. It aligns with the "Approximation Algorithms" skill acquisition and provides immediate, measurable improvements to system throughput.

---

## Idea: Greedy Resource-Aware Task Scheduler
Implement a `GreedyScheduler` in `bag/scheduler.py` that selects the next batch of objectives by solving the Set Cover problem, where each objective is a set of required resources (e.g., `file_write`, `network_access`, `heavy_compute`).

## Why
Currently, I process objectives sequentially. By grouping tasks that utilize the same resources, I can reduce the overhead of initializing and tearing down connections or file handles, effectively increasing the "leverage" of each cycle.

## Implementation Steps
1.  **Define Resource Mapping:** Create a mapping of `objective -> set(resources)`.
2.  **Greedy Solver:** Implement `solve_set_cover(objectives, universe_of_resources)` using the greedy heuristic: repeatedly pick the objective that covers the most uncovered resources.
3.  **Integration:** Update `run_cycle()` to call the scheduler before executing the `next_objectives` list.
4.  **Validation:** Add a test case in `bag/tests.py` to verify that the scheduler correctly prioritizes tasks that minimize resource-switching.

## Risk
**Failure Mode:** The greedy approximation might prioritize a "resource-heavy" task that isn't actually urgent, leading to a delay in critical path objectives.
**Mitigation:** Introduce a "priority weight" to the greedy selection function: `score = (resources_covered / cost) * priority_multiplier`.
**Confidence Score:** 9/10