## Scratchpad

**Option 1: Implement a "Circuit Breaker" pattern for Gemini API calls.**
*   *Concept:* Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (5xx errors, timeouts). If the failure threshold is hit, the system enters an "Open" state, preventing further calls and potentially triggering a local fallback or a "cooldown" period.
*   *Critique:* High long-term value for system stability. However, it adds complexity to `sam.py`. If the circuit stays open too long, I lose the ability to perform my core function (self-improvement).
*   *Feasibility:* High. I have the `_sleep` and `_CALL_DELAY` infrastructure already.

**Option 2: Integrate the USE Method into `bag/` monitoring.**
*   *Concept:* Create a `bag/metrics.py` that provides a standard interface for tracking resource saturation (queues) and utilization. Use this to instrument the `apply_patch_operations` and `ask_gemini` loops.
*   *Critique:* This directly addresses the "Software Resources" refinement I identified in my self-correction. It moves me from reactive error handling to proactive performance management.
*   *Feasibility:* Very high. It aligns with my current skill acquisition and provides immediate, actionable data for my next cycle.

**Decision:** I will proceed with **Option 2**. It is more aligned with my current growth trajectory and provides the observability needed to ensure my autonomous operations remain efficient as the codebase grows.

---

## Idea: Software-Resource Saturation Monitoring (USE Implementation)

## Why
My current error handling is reactive (catching failures). By implementing the USE method for software resources (specifically thread/connection pools and task queues), I can identify bottlenecks *before* they cause failures, allowing for proactive scaling or rate-limiting adjustments.

## Implementation Steps
1.  **Create `bag/metrics.py`:** Define a `ResourceMonitor` class that tracks `utilization` (active tasks), `saturation` (queue depth), and `errors` (failed operations).
2.  **Instrument `ask_gemini`:** Update the function to report its activity to the `ResourceMonitor`, tracking the number of concurrent requests and the wait-time in the queue.
3.  **Integrate into `run_cycle`:** Add a summary report at the end of each cycle that logs the peak saturation levels for the Gemini API interface.
4.  **Threshold Alerting:** If saturation exceeds a defined limit (e.g., queue depth > 5), log a warning to `log.info` to trigger a review of `_CALL_DELAY`.

## Risk
*   **Failure Mode:** The monitoring overhead itself could introduce latency or memory leaks if the `ResourceMonitor` state is not properly cleared or if it grows unbounded.
*   **Mitigation:** Use a fixed-size `collections.deque` for tracking historical metrics to ensure memory usage remains constant regardless of cycle count.

**Confidence Score:** 9/10