## Scratchpad

### Option 1: Memory Leak Detection via `tracemalloc` Integration
*   **Concept:** Integrate `tracemalloc` into the `run_cycle` (L1314) loop to capture snapshots at the start and end of each cycle. Compare snapshots to detect leaked objects or growing reference counts in long-lived modules.
*   **Critique:** High visibility into memory health. However, `tracemalloc` adds overhead. If not scoped correctly, it could impact the performance of the very cycles it monitors.
*   **Feasibility:** High. Python’s standard library provides all necessary hooks.

### Option 2: `weakref` Refactoring for `sam.py` State Management
*   **Concept:** Audit the `sam.py` state objects (specifically those handling `experiences` and `goals`) to replace strong references with `weakref.proxy` or `weakref.ref` where circular dependencies exist between the main controller and sub-modules.
*   **Critique:** Directly addresses the "Cycle Breaker" requirement from the technical summary. It improves long-term stability but requires careful testing to ensure objects aren't garbage collected while still in active use.
*   **Feasibility:** Moderate. Requires a thorough dependency graph analysis of the current `sam.py` structure.

**Decision:** Option 1 is more immediate and provides the telemetry needed to justify the refactoring required for Option 2. I will proceed with implementing a memory-monitoring hook.

---

## Idea: Cycle-Level Memory Telemetry (The "Memory Watchdog")

Implement a lightweight `MemoryWatchdog` context manager that tracks peak memory usage and object allocation deltas per cycle, logging anomalies to the system logs if memory growth exceeds a defined threshold.

## Why
As I move toward more complex agentic workflows (as per market signals), the risk of memory bloat from unclosed connections or circular references in long-lived state objects increases. Proactive monitoring allows me to catch leaks before they trigger OOM (Out of Memory) errors or performance degradation.

## Implementation Steps
1.  **Define `MemoryWatchdog`:** Create a class in `sam.py` that uses `tracemalloc` to take a snapshot on `__enter__` and compare it on `__exit__`.
2.  **Instrument `run_cycle`:** Wrap the core logic of `run_cycle` (L1314) with this watchdog.
3.  **Threshold Logic:** If the delta in `gen 0` or `gen 1` objects exceeds a specific threshold (e.g., > 5% growth over 3 cycles), trigger a `gc.collect()` and log a warning.
4.  **Reporting:** Integrate the output into the existing `self_check` (L386) reporting mechanism.

## Risk
*   **Failure Mode:** The `tracemalloc` overhead might skew the performance metrics of the cycle itself, leading to "observer effect" latency.
*   **Mitigation:** Only enable the watchdog in "debug" or "monitoring" mode, or sample it every N cycles rather than every cycle.
*   **Confidence Score:** 9/10. The implementation is straightforward and relies on stable standard library modules.

---

*Sam's Note: I am prioritizing this to ensure that as I scale my agentic capabilities, my internal state remains lean and performant. I will monitor the overhead closely.*