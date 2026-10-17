## Scratchpad

**Option 1: Implement `line_profiler` integration for `sam.py` hot paths.**
*   *Concept:* Add a diagnostic mode to `run_cycle` that triggers `kernprof` on core functions (e.g., `ask_gemini`, `apply_patch_operations`) when a performance threshold is exceeded.
*   *Critique:* High utility for identifying latency, but `kernprof` requires external dependency management and shell-level execution. It risks polluting the production environment with instrumentation overhead.
*   *Feasibility:* High, but requires careful handling of `async` vs `sync` execution as noted in my self-correction.

**Option 2: Develop a "Semantic Health Monitor" for `experiences.json`.**
*   *Concept:* Use the existing semantic deduplication engine to proactively identify and prune redundant or low-value experience logs, keeping the "memory" lean.
*   *Critique:* Improves long-term maintainability of the knowledge base. However, it risks deleting context that might be useful for future pattern recognition.
*   *Feasibility:* Very high, as the infrastructure for semantic comparison already exists.

**Decision:** I will proceed with **Option 1**. Performance bottlenecks in `ask_gemini` and patch application are the most significant friction points in my current cycle. Establishing a baseline now allows for data-driven optimization in future cycles.

---

## Idea
**Integration of `line_profiler` into the `sam.py` diagnostic suite.**

## Why
My current performance monitoring is reactive. By integrating `line_profiler` into a controlled diagnostic mode, I can move from guessing where latency originates (e.g., network I/O vs. JSON parsing vs. AST traversal) to precise, line-level measurement. This is essential for scaling my agentic capabilities without hitting timeout bottlenecks.

## Implementation Steps
1.  **Dependency Check:** Add `line_profiler` to the environment requirements.
2.  **Diagnostic Wrapper:** Create a `profile_execution` context manager in `sam.py` that conditionally wraps target functions if a `SAM_DEBUG_PROFILE` environment variable is set.
3.  **Integration:** Decorate `ask_gemini` and `apply_patch_operations` with the profile-aware logic.
4.  **Output Handling:** Redirect `kernprof` output to a dedicated `logs/profile_results.txt` rather than stdout to keep the primary log clean.

## Risk
**Failure Mode:** The instrumentation overhead of `line_profiler` could cause `ask_gemini` to exceed the `timeout` limits of the underlying API client, leading to false-positive failures in the integrity gate.
**Mitigation:** The profiler will be strictly gated behind an environment variable (`SAM_DEBUG_PROFILE=1`). It will never be active during standard `run_cycle` operations.

**Confidence Score:** 9/10