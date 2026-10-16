## Scratchpad

**Option 1: Memory-Budgeted CI Gate**
*   **Concept:** Integrate `memray` into the `self_check()` workflow to enforce a hard memory ceiling (e.g., 50MB) on core modules.
*   **Critique:** High feasibility. It directly addresses the "Action Items" from the recent skill acquisition. It provides a quantitative guardrail against memory bloat.
*   **Trade-off:** Adds overhead to the integrity gate. If the threshold is too tight, it may trigger false-positive rollbacks during complex operations.

**Option 2: GraphRAG-lite for Experience Logs**
*   **Concept:** Implement a simple entity-relationship extraction for `experiences.json` to move beyond flat list storage, enabling better semantic retrieval for the Spaced Repetition engine.
*   **Critique:** High complexity. Requires building a schema for the graph and updating the `phase_ii_spaced_repetition` logic.
*   **Trade-off:** Significant long-term benefit for memory recall, but risks over-engineering if the current flat structure is still performant.

**Selection:** Option 1 is the superior choice for this cycle. It aligns with my current focus on architectural stability and provides immediate, measurable feedback on system health, fulfilling the "Minimal footprint, maximum leverage" core trait.

---

## Idea: Memory-Budgeted Integrity Gate (`memray` integration)

## Why
My current `self_check()` validates syntax and logic, but it is blind to resource consumption. As I integrate more complex agentic frameworks, I need an automated "resource budget" to prevent memory leaks from degrading performance before they become critical.

## Implementation Steps
1.  **Dependency Check:** Verify `memray` is available in the environment; if not, log a warning and skip memory profiling (graceful degradation).
2.  **Wrapper Implementation:** Create `bag/perf_utils.py` with a `profile_memory(func, threshold_mb)` decorator.
3.  **Integrity Gate Update:** Modify `self_check()` in `sam.py` to execute a representative subset of core modules (e.g., `ask_gemini` logic) wrapped in the memory profiler.
4.  **Threshold Enforcement:** If `memray` reports a peak allocation exceeding the threshold, trigger an `_alert_dot` with the generated flame graph path and rollback to the last known stable state.

## Risk
**Failure Mode:** The profiling overhead might cause the `self_check()` to exceed its 20-second timeout, leading to a false-positive rollback.
**Mitigation:** Use `memray`'s sampling mode or restrict profiling to a single, high-risk module per cycle rather than the entire suite.

**Confidence Score:** 9/10