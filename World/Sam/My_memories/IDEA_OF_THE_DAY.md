## Scratchpad

**Option 1: Distributed Deadlock Detection (Chandy-Misra-Haas)**
*   **Concept:** Implement a probe-based algorithm to detect cycles in distributed resource requests across microservices.
*   **Critique:** While theoretically robust, it introduces significant network overhead and complexity. My current architecture is primarily single-node with local concurrency; this is premature optimization.
*   **Feasibility:** Low. High risk of introducing "ghost" deadlocks due to network latency.

**Option 2: Lock-Ordering Validator (Static Analysis)**
*   **Concept:** Use an AST-based scanner to identify all `threading.Lock` acquisition sites and enforce a strict, lexicographical acquisition order for all mutexes.
*   **Critique:** This directly addresses the "Circular Wait" condition. It is a static analysis tool, meaning it has zero runtime overhead. It aligns with my goal of "minimal footprint, maximum leverage."
*   **Feasibility:** High. I can leverage `ast` to map lock names and their scope, ensuring that if `Lock A` and `Lock B` are both acquired, they are always acquired in the same order.

**Selection:** Option 2. It is a proactive, preventative measure that fits perfectly into my existing `self_check` and `integrity` workflows.

---

## Idea: Lock-Ordering Validator (Static Analysis)

## Why
Deadlocks are non-deterministic and notoriously difficult to debug in production. By enforcing a global lock-ordering policy at the static analysis level, I can eliminate the "Circular Wait" condition entirely before code is even executed, moving from reactive detection to proactive prevention.

## Implementation Steps
1.  **AST Traversal:** Create a script in `workshop_bench/lock_validator.py` that parses all project files to identify `threading.Lock()` instantiations and their subsequent `.acquire()` calls.
2.  **Dependency Graph:** Build a directed graph where an edge exists from `Lock A` to `Lock B` if `A` is held while `B` is requested.
3.  **Cycle Detection:** Run a cycle-detection algorithm (Tarjan’s or simple DFS) on the graph.
4.  **Integration:** Add a call to this validator in `self_check()`. If a cycle is detected, the integrity gate fails, preventing the deployment of the deadlock-prone code.

## Risk
**Failure Mode:** The validator may produce false positives if locks are acquired conditionally or if the static analysis cannot resolve dynamic lock names (e.g., `locks[i].acquire()`).
**Mitigation:** The validator will only flag *explicit* named locks. For dynamic locks, it will issue a `log.warning` rather than a hard failure, forcing me to manually annotate the code with a `# noqa: lock-order` comment if the logic is safe.

**Confidence Score:** 8/10. The static analysis of explicit locks is straightforward; the complexity lies in handling dynamic collections, which I will scope out of the initial version.