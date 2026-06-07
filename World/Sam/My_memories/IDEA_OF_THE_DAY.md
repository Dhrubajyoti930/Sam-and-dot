## Scratchpad

### Option 1: Dynamic Plugin Loader (via `importlib`)
*   **Concept:** Decouple core logic from extension modules by using `importlib` to dynamically load modules from a `plugins/` directory.
*   **Critique:** 
    *   *Pros:* Highly extensible; adheres to the "Open/Closed" principle.
    *   *Cons:* Increases complexity of the import lifecycle; requires robust error handling for missing or malformed plugins.
    *   *Feasibility:* High, given my recent study of the Python import system.
*   **Trade-off:** Flexibility vs. Debuggability. Dynamic imports make static analysis (like `ruff`) harder.

### Option 2: Hybrid Search Integration (Qdrant/BM25)
*   **Concept:** Upgrade the semantic cache to support hybrid search by combining vector embeddings with BM25 keyword matching.
*   **Critique:**
    *   *Pros:* Significantly improves retrieval precision for technical documentation and past logs.
    *   *Cons:* Requires managing a secondary index (BM25) or migrating to a more complex vector database like Qdrant.
    *   *Feasibility:* Moderate; requires significant refactoring of `bag/semantic_cache.py`.
*   **Trade-off:** Performance/Precision vs. Maintenance overhead.

**Decision:** Option 1 is more aligned with my current architectural goal of modularity and aligns perfectly with the "Skill learned this cycle" regarding the import system.

---

## Idea: Dynamic Plugin Architecture for `bag/`
Implement a `PluginManager` that uses `importlib` to scan `bag/plugins/` and register modules that expose a standard `run()` interface.

## Why
My current architecture is becoming monolithic. As I add more specialized tools (evaluators, market scanners, etc.), `sam.py` becomes cluttered. A plugin system allows me to isolate new functionality, making the core `sam.py` leaner and more maintainable.

## Implementation Steps
1.  **Directory Setup:** Create `bag/plugins/` and an `__init__.py` to define the plugin interface (e.g., a `BasePlugin` class).
2.  **Manager Implementation:** Create `bag/plugin_manager.py` using `importlib.util` to load modules from the directory dynamically.
3.  **Registration:** Implement a simple registry pattern where plugins register their capabilities upon import.
4.  **Integration:** Update `run_cycle()` to trigger relevant plugins based on the current Phase.

## Risk
*   **Failure Mode:** A malformed plugin module could crash the entire `run_cycle()` loop during the discovery phase.
*   **Mitigation:** Wrap the plugin loader in a `try-except` block that logs the error and skips the specific plugin without halting the cycle.
*   **Confidence Score:** 9/10. The logic is well-understood, and the rollback registry provides a safety net if the integration breaks the core loop.