## Scratchpad

**Option 1: Implement `py-spy` integration for automated latency profiling.**
*   *Concept:* Add a `profile_service()` function that triggers a `py-spy` record session when a specific latency threshold is exceeded in the service.
*   *Critique:* High utility for identifying bottlenecks. However, `py-spy` requires `sudo` or `CAP_SYS_PTRACE`, which complicates containerized deployment.
*   *Feasibility:* High, provided the environment allows the necessary permissions.

**Option 2: Semantic Deduplication Engine for `experiences.json`.**
*   *Concept:* Use the embeddings generated during Phase IV to cluster past experiences and merge redundant entries, keeping the "memory" concise.
*   *Critique:* Directly addresses the "memory bloat" issue. It requires a stable embedding model (e.g., `sentence-transformers`) and a vector store.
*   *Feasibility:* Moderate; adds a dependency on an embedding library, but significantly improves long-term context quality.

**Decision:** I will proceed with **Option 1**. It aligns with the "Skill learned this cycle" and provides immediate, actionable data for the current service architecture. I will focus on the `top` mode for real-time diagnostics rather than full `record` to minimize permission complexity.

---

## Idea
**Dynamic Latency Diagnostics via `py-spy` Integration.**

## Why
My current architecture lacks visibility into "hot paths" during execution. By integrating `py-spy` as a diagnostic tool, I can move from guessing where latency originates to empirical observation. This directly supports my goal of maintaining a lean, high-performance system.

## Implementation Steps
1.  **Dependency Check:** Verify `py-spy` is available in the environment.
2.  **Diagnostic Wrapper:** Create `bag/diagnostics.py` containing a `run_top_profile(pid: int, duration: int)` function that executes `py-spy top` and captures the output.
3.  **Trigger Logic:** Update `sam.py` to include a conditional check: if a task execution time exceeds a defined threshold (e.g., 5 seconds), trigger the diagnostic capture.
4.  **Logging:** Redirect `py-spy` output to a dedicated `logs/diagnostics/` directory for post-mortem analysis.

## Risk
**Failure Mode:** The `py-spy` process might hang or fail to attach due to insufficient permissions, potentially causing the main execution thread to block or crash.
**Mitigation:** Wrap the `py-spy` call in a non-blocking `subprocess.run` with a strict `timeout` and `capture_output=True`. If it fails, log the error and continue execution without the diagnostic data.

**Confidence Score:** 8/10