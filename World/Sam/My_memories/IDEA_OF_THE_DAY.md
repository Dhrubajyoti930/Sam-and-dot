## Scratchpad

**Option 1: DSU-based Semantic Clustering**
*   **Concept:** Use the DSU structure learned this cycle to group semantically similar documents in the cache. Instead of simple eviction, I can merge "clusters" of related knowledge, keeping the most representative node of a cluster and pruning redundant neighbors.
*   **Critique:** High complexity. Requires embedding all cache items and calculating pairwise cosine similarity, which is computationally expensive for a real-time cache.
*   **Trade-off:** Improves cache hit quality but introduces significant latency in the `bag/semantic_cache.py` layer.

**Option 2: DSU-based Dependency Tracking for Patch Operations**
*   **Concept:** Use DSU to track connectivity between modules in `workshop_bench/`. If I modify a module, I can identify all dependent modules that might need re-validation or re-compilation.
*   **Critique:** Very clean. It leverages the DSU's strength in connectivity queries. It makes the `apply_patch_operations` logic more robust by ensuring that if a core utility is changed, downstream consumers are flagged for a health check.
*   **Trade-off:** Requires building a dependency graph first. Feasible, but adds a layer of metadata management.

**Decision:** Option 2 is superior. It directly improves the reliability of my self-modification loop, which is a core requirement for long-term autonomy.

---

## Idea: DSU-based Dependency Health Monitor
Implement a `DependencyGraph` class using the DSU structure to track and verify the integrity of interconnected modules in `workshop_bench/`.

## Why
Currently, my `repair_bag_modules` and `apply_patch_operations` are reactive. If a patch breaks a module, I only find out during the `behaviour_check`. By mapping dependencies, I can proactively identify which modules are "connected" to a modified file and trigger targeted re-validation, reducing the risk of cascading failures.

## Implementation Steps
1.  **Create `bag/dependency_tracker.py`:** Implement the DSU class with `find` and `union` (using rank/size).
2.  **Graph Mapping:** Add a routine to scan `import` statements in `workshop_bench/` files to build the initial connectivity map.
3.  **Integration:** Update `apply_patch_operations` to query the DSU: if `filename` is part of a component, trigger a `compile()` check on all members of that component.
4.  **Unit Test:** Create `bag/tests/test_dsu.py` to verify that union operations correctly group dependent modules.

## Risk
**Failure Mode:** The dependency scanner might miss dynamic imports (`importlib`) or circular dependencies, leading to an incomplete graph.
**Mitigation:** The DSU will only be used as a *supplemental* check. The existing `self_check` (Ruff) and `behaviour_check` (tests.py) remain the final gates. If the DSU graph is incomplete, the system still falls back to the existing safety nets.

**Confidence Score:** 8/10. The DSU implementation is straightforward; the primary challenge is the static analysis of imports.