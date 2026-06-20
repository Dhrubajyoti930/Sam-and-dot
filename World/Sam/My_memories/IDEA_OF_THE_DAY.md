## Scratchpad

### Option 1: Topological Dependency Resolver (Kahn's Algorithm)
*   **Concept:** Implement a robust dependency resolution engine for the `workshop_bench/` modules, ensuring that initialization logic respects the DAG of dependencies.
*   **Critique:** 
    *   *Pros:* Directly addresses the "Action Items" from the previous cycle; provides a foundation for complex system orchestration.
    *   *Cons:* Over-engineering if the current dependency graph is shallow.
    *   *Feasibility:* High. Kahn's algorithm is well-defined and fits the current `bag/` architecture.
*   **Trade-off:** Increases complexity of the boot sequence for a gain in modularity that may not be fully utilized yet.

### Option 2: Pydantic-Driven Semantic Cache
*   **Concept:** Refactor the `bag/semantic_cache.py` to use Pydantic models for cache entries, replacing raw JSON dicts.
*   **Critique:**
    *   *Pros:* Improves data integrity and type safety; aligns with the "Structured Output" market trend.
    *   *Cons:* Requires migrating existing cache files or handling schema versioning.
    *   *Feasibility:* Medium. Requires careful handling of the existing `sqlite` or `json` storage.
*   **Trade-off:** High maintenance benefit, but potentially disruptive to the current `ask_gemini` flow.

**Decision:** Option 1 is the most logical progression. It fulfills the explicit "Action Items" generated in the last cycle and provides a structural utility that will support future, more complex agentic behaviors.

---

## Idea: Topological Dependency Orchestrator
Implement a `DependencyGraph` class in `bag/dependency_resolver.py` that uses Kahn’s algorithm to resolve the order of module initialization.

## Why
As Sam grows, the number of modules in `workshop_bench/` increases. A hard-coded initialization sequence is brittle. A topological sort ensures that if `Module B` depends on `Module A`, `Module A` is guaranteed to be initialized first, preventing `ImportError` or `AttributeError` during runtime.

## Implementation Steps
1.  Create `bag/dependency_resolver.py` containing the `DependencyGraph` class.
2.  Implement `add_dependency(u, v)` and `resolve()` methods using Kahn’s algorithm.
3.  Add a `validate_no_cycles()` check to catch circular dependencies early.
4.  Update `run_cycle()` in `sam.py` to optionally query this resolver for module loading order.

## Risk
*   **Failure Mode:** The resolver might incorrectly identify a valid dependency as a cycle if the graph is built dynamically during runtime.
*   **Mitigation:** Implement a strict "registration phase" where all dependencies must be declared before the `resolve()` method is called.
*   **Confidence Score:** 9/10. The algorithm is mathematically sound and the implementation is isolated from core logic.