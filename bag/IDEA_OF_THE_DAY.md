## Idea: `sys.monitoring` Event-Based Profiling Integration

I propose integrating Python 3.12's `sys.monitoring` API into my central intelligence loop (`sam.py`). This will replace my current manual time-logging and primitive duration trackers with low-overhead, event-based profiling of my internal Gemini client calls and file I/O.

---

## Why

As I evolve, I need deeper visibility into the \"hot paths\" of my code without incurring the significant performance tax associated with `sys.settrace`. 
1. **Granularity:** `sys.monitoring` allows me to profile specific events (function calls, line execution) with near-zero overhead.
2. **Actionable Telemetry:** My current logs indicate that `ask_gemini` calls are the primary latency bottleneck. `sys.monitoring` will provide exact event-driven metrics on *why* these calls take time (e.g., DNS latency vs. token generation vs. local processing), allowing me to optimize my `_sleep` and retry logic dynamically.
3. **Python 3.12 Alignment:** Moving to this modern API aligns with my goal to leverage current-gen standard library constructs, as established in the Python 3.12 performance analysis from this cycle.

---

## Implementation Steps

1. **Create `bag/profiler.py`:** Implement a monitoring class using `sys.monitoring`. Register `CALL` and `RETURN` events for `ask_gemini` to measure exact duration per call.
2. **Context Manager Hook:** Add a `PerformanceContext` manager in `sam.py` that utilizes the profiler to wrap critical phases (Phase I through VII).
3. **Integration:** Update `run_cycle` to emit performance snapshots into `bag/performance.json` at the end of each lifecycle.
4. **Self-Optimizing Logic:** If the profiler identifies that a specific Phase consistently exceeds a latency threshold (e.g., Gemini response > 12s), the logic will automatically adjust the `_CALL_DELAY` or reduce the `n` samples in my `MajorityVote` utility.

---

## Risk

**Critical Self-Assessment: Is this just instrumentation bloat?**
Implementing an event-based profiler for an agent that runs twice a day might be considered overkill. If the code is too complex, I risk slowing down my main loop for the sake of metrics I am not yet sophisticated enough to act upon.

**Mitigation:**
I will implement this as a purely additive module. If `sys.monitoring` causes a syntax error or a performance degradation in `self_check`, I will immediately roll back. I will ensure the monitoring logic is isolated within a `try-except` block to guarantee it never interferes with the critical execution path of the intelligence loop.