## Idea: Latency-Aware Automated Rollback Trigger (LART)

I propose implementing a **Latency-Aware Automated Rollback Trigger (LART)** in `sam.py`. This utility will use the latency data collected by `sys.monitoring` to automatically revert any self-modification patch if the average execution time of the affected module increases by $>30\%$ compared to its historical moving average within the first 3 cycles of deployment.

---

## Why

My current self-correction relies on syntax (`compile`) and behavioral (`tests.py`) checks, but I have no protection against **performance degradation**.
1. **Silent Regression:** A patch can be syntactically correct and pass unit tests, yet introduce subtle performance bottlenecks (e.g., inefficient loop operations, excessive I/O, or redundant deep-copying) that silently degrade my operational velocity.
2. **Resource Hygiene:** My Kaizen loop requires constant improvement. If a self-modifying refactor makes me slower, it is a net failure, even if it adds features.
3. **Automated Vigilance:** Manually reviewing `sam.log` for performance dips is slow. An automated rollback trigger ensures that any performance-degrading modification is caught and purged without requiring human (Dot) intervention.

---

## Implementation Steps

1. **Instrumentation:** Modify `bag/profiler.py` to store a rolling moving average of execution duration per module (file-level granularity).
2. **Trigger Logic:** Add a check in `apply_self_modification` that runs after the `behaviour_check()`.
   - The trigger calculates: $Delta = \frac{Current\_Latency - Historic\_Latency}{Historic\_Latency}$.
   - If $Delta > 0.30$, flag for a performance rollback.
3. **Rollback:** If flagged, execute the `_rollback()` function and write an alert to `motion.md` explaining the performance regression.
4. **Grace Period:** Implement a 3-cycle grace period for *new* modules to allow the system to establish a baseline performance before triggering rollbacks.

---

## Risk

**Critical Self-Assessment:** 
Is this a \"perf-regression nightmare\" waiting to happen? External factors (Gemini API latency, system load, network jitter) can easily spike execution time by $30\%$, triggering an unnecessary rollback of a perfectly functional patch.

**Mitigation:**
- **Jitter Buffer:** The trigger will only fire if the latency threshold is breached across 3 consecutive calls, filtering out transient network spikes.
- **Log-First:** I will log \"Performance Regression Detected\" warnings to `sam.log` for 5 cycles before enabling the autonomous rollback trigger.
- **Manual Bypass:** I will add a `manual_override` flag in `goals.json`. If Dot determines a performance-degrading change is nonetheless desirable (e.g., it adds essential safety), he can force the system to ignore the regression.