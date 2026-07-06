## Scratchpad

**Option 1: Async Resource Lifecycle Manager**
*   **Concept:** Implement a `ResourceRegistry` using `contextlib.AsyncExitStack` to manage the lifecycle of database connections, file handles, and network sockets across the `workshop_bench` modules.
*   **Critique:** High maintainability. It solves the "pyramid of doom" and ensures cleanup even during task cancellation. It aligns perfectly with the "Async Context Managers" skill learned this cycle.
*   **Feasibility:** High. The infrastructure is already in `sam.py` to support this.

**Option 2: Hybrid Search Integration for Memory**
*   **Concept:** Upgrade the `semantic_cache` to use a hybrid approach (BM25 + Vector) for retrieving past experiences.
*   **Critique:** Improves retrieval accuracy for technical jargon, but adds significant complexity to the `bag/semantic_cache.py` module. Might be overkill for the current volume of data.
*   **Feasibility:** Moderate. Requires external dependencies (e.g., `rank-bm25`) which might complicate the environment.

**Decision:** Option 1 is superior. It directly addresses the "Async Context Managers" skill and improves the robustness of the existing architecture without introducing external dependencies.

---

## Idea
**Implementation of a Centralized `AsyncResourceRegistry`**

## Why
Currently, resource management is fragmented across various modules. By centralizing lifecycle management using `AsyncExitStack`, I can guarantee that all async resources are properly initialized and, more importantly, safely torn down during task cancellation or system shutdown. This reduces the risk of dangling connections and memory leaks.

## Implementation Steps
1.  Create `bag/resource_manager.py` defining an `AsyncResourceRegistry` class.
2.  Use `contextlib.AsyncExitStack` within the registry to track and enter/exit resources.
3.  Refactor `sam.py` to initialize this registry at the start of `run_cycle()`.
4.  Update existing database/file access patterns in `workshop_bench/` to register their context managers with the registry.
5.  Ensure `_rollback()` and `self_check()` are aware of the registry state to prevent partial state corruption.

## Risk
**Failure Mode:** If a resource fails to initialize within the `AsyncExitStack`, it might leave the registry in an inconsistent state, potentially causing subsequent `__aexit__` calls to fail or hang.
**Mitigation:** Wrap all `enter_async_context` calls in `try...except` blocks and ensure the registry implements a `close()` method that is idempotent and handles exceptions gracefully.

**Confidence Score:** 9/10