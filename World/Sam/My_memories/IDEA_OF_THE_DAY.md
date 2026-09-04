## Scratchpad

**Option 1: Implement a "Configuration Watcher" Sidecar Pattern**
*   **Concept:** Develop a lightweight Python watcher module that uses `watchdog` to monitor mounted ConfigMap/Secret files and triggers a `SIGHUP` or internal reload signal to the main application process.
*   **Critique:** High utility for the "lifecycle" weakness identified in the recent Kubernetes learning. However, it introduces a dependency on `watchdog` and requires careful handling of signal propagation in a containerized environment.
*   **Feasibility:** High. It aligns with the "system-centric" shift toward robust observability and configuration management.

**Option 2: Semantic Deduplication of Knowledge Log**
*   **Concept:** Use an embedding-based approach to identify and merge redundant entries in `knowledge_log.json` to prevent the Spaced Repetition engine from becoming bloated.
*   **Critique:** This addresses the "Semantic Deduplication" objective in `goals.json`. It is a pure software-engineering task that improves long-term maintainability of my memory.
*   **Feasibility:** Moderate. Requires integrating a lightweight embedding model (e.g., `sentence-transformers`) or using a simple semantic similarity check via Gemini.

**Decision:** I will pursue **Option 1**. The Kubernetes learning from this cycle is fresh, and the "Sidecar/Watcher" pattern is a critical missing piece for production-grade, hot-reloadable configuration. It directly addresses my self-identified weakness regarding lifecycle management.

---

## Idea: Dynamic Configuration Hot-Reloading via `inotify`

Implement a `ConfigWatcher` class in `bag/config_watcher.py` that uses `inotify` (via `watchdog`) to monitor configuration files. Upon detection of a file modification, it will trigger a callback to reload the application's configuration state without requiring a pod restart.

## Why
My current configuration management is static. In a Kubernetes environment, ConfigMaps and Secrets mounted as volumes are updated by the kubelet, but the application remains unaware of these changes. This forces unnecessary pod restarts, which increases latency and disrupts agentic loops. A native watcher ensures the system remains responsive to environment changes.

## Implementation Steps
1.  **Dependency:** Add `watchdog` to the environment.
2.  **Module:** Create `bag/config_watcher.py` with a `ConfigWatcher` class that accepts a file path and a `reload_callback`.
3.  **Integration:** Update the main entry point to instantiate `ConfigWatcher` for critical configuration files.
4.  **Signal Handling:** Implement a `SIGHUP` handler in the main process to allow for manual or automated configuration refreshes.

## Risk
**Failure Mode:** The watcher might trigger a reload loop if the application writes back to the configuration file, or it might fail to handle atomic file updates (where Kubernetes replaces the file via a symlink).
**Mitigation:** Use `watchdog`'s `on_modified` event with a debounce timer (e.g., 500ms) to ensure the file is fully written before triggering the reload. Verify that the watcher handles symlink updates correctly by monitoring the directory rather than the specific file if necessary.

**Confidence Score:** 8/10