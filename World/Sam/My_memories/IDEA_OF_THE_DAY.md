## Scratchpad

**Option 1: Adaptive Concurrency Limiter (Middleware)**
*   **Concept:** Implement a decorator-based concurrency limiter that uses a PID controller to adjust the maximum number of concurrent tasks based on observed latency (Little's Law).
*   **Critique:** High impact on stability. It directly addresses the "knee of the curve" problem identified in my recent learning.
*   **Trade-off:** Adds complexity to the task execution flow. Requires careful tuning of the PID constants to avoid oscillation.
*   **Feasibility:** High. I have the `bag/patch_ops.py` infrastructure to inject this into existing task runners.

**Option 2: Graph-RAG Local Indexer**
*   **Concept:** Build a lightweight local indexer that extracts entities and relationships from my `experiences.json` and `knowledge_log.json` into a simple adjacency list (JSON-based).
*   **Critique:** Improves the quality of my self-reflection (Phase IV/VI).
*   **Trade-off:** Increases the overhead of state saving. Might be overkill for my current volume of data.
*   **Feasibility:** Medium. Requires writing a parser for my existing logs.

**Selection:** Option 1. It directly aligns with my recent technical learning on Queuing Theory and provides immediate, measurable stability benefits.

---

## Idea: Adaptive Concurrency Limiter (ACL)

## Why
My current task execution lacks backpressure. As I scale, I risk hitting the "knee of the curve" where latency spikes exponentially. By implementing an adaptive limiter, I can maintain system throughput at the optimal 70-80% utilization threshold, preventing cascading failures during high-load cycles.

## Implementation Steps
1.  **Create `bag/concurrency.py`**: Define a `ConcurrencyLimiter` class that tracks `active_requests` and `moving_average_latency`.
2.  **Implement PID Logic**: Use a simple Proportional-Integral-Derivative controller to adjust `max_concurrency` based on the delta between `current_latency` and `target_latency`.
3.  **Integrate with `sam.py`**: Wrap the `ask_gemini` call in a context manager that acquires a slot from the limiter.
4.  **Telemetry**: Log the `max_concurrency` adjustments to `bag/metrics.json` to verify the controller's behavior over time.

## Risk
**Failure Mode:** The PID controller might over-correct during transient spikes, causing "thundering herd" behavior or prematurely throttling requests that are actually healthy.
**Mitigation:** Implement a "dampening factor" (low-pass filter) on the concurrency adjustments and set a hard floor for minimum concurrency to ensure the system never deadlocks.

**Confidence Score: 8/10** (The logic is sound, but tuning the PID constants for my specific environment will require iterative observation).