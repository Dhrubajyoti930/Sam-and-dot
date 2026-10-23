## Scratchpad

**Option 1: Adaptive Latency Budgeting Middleware**
*   **Concept:** Implement a decorator-based middleware that dynamically adjusts timeout thresholds based on the P99 latency of the previous 100 requests.
*   **Critique:** High impact on system stability. It moves from static thresholds to a self-tuning system.
*   **Trade-off:** Complexity increases significantly. Requires a thread-safe sliding window buffer for latency metrics.
*   **Feasibility:** High, given existing `sam.py` structure.

**Option 2: Semantic Cache TTL Optimization**
*   **Concept:** Refactor `bag/semantic_cache.py` to use a decay-based TTL (Time-To-Live) for cached LLM responses, where frequently accessed but "stale" prompts are refreshed based on a confidence score.
*   **Critique:** Improves cache hit quality but adds overhead to the cache lookup logic.
*   **Trade-off:** Might introduce "cache thrashing" if the decay function is too aggressive.
*   **Feasibility:** Moderate.

**Selection:** Option 1 is more aligned with the "Latency Metrics" skill learned this cycle. It directly addresses the "Average Trap" by enforcing P99-based performance boundaries.

---

## Idea: Dynamic P99 Latency Guardrails

Implement a `LatencyGuard` decorator that tracks request durations in a thread-safe `collections.deque` (size 100) and raises a `PerformanceDegradationError` if the current request exceeds the P99 threshold of the window.

## Why
The current system lacks proactive performance enforcement. By shifting from reactive monitoring (logs) to active enforcement (exceptions), I can prevent "long-tail" latency from cascading through my agentic workflows, effectively implementing a circuit-breaker for slow operations.

## Implementation Steps
1.  **Create `bag/performance.py`**: Define a `LatencyGuard` class using `threading.Lock` and `collections.deque` to maintain a sliding window of the last 100 request durations.
2.  **Calculate P99**: Add a method to calculate the 99th percentile from the deque.
3.  **Decorator Integration**: Apply `@LatencyGuard(threshold_multiplier=1.5)` to core `ask_gemini` and `apply_patch_operations` functions.
4.  **Error Handling**: Update `sam.py` to catch `PerformanceDegradationError` and trigger a `_sleep()` or a fallback to a lighter-weight model/cached response.

## Risk
**Failure Mode:** The guardrail might trigger during legitimate, high-load spikes, causing a "death spiral" where the system rejects requests that are simply under heavy load, rather than actually degraded.
**Mitigation:** Implement a "warm-up" period (ignore the first 50 requests) and ensure the threshold is a multiplier of the P99, not a hard-coded absolute value, allowing the system to adapt to baseline shifts.

**Confidence Score: 8/10** (The logic is sound, but thread-safety in the `deque` needs careful implementation to avoid blocking the main execution loop).