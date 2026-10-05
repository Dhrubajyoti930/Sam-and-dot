## Scratchpad

### Option 1: Implementing a "Circuit Breaker" for Gemini API Calls
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that tracks failure rates (timeouts, 5xx errors, truncation loops). If the error rate exceeds a threshold, the system enters an "Open" state, forcing a cooldown period or falling back to a local SLM (e.g., a quantized Llama-3-8B via `llama.cpp`).
*   **Critique:** High feasibility. It directly addresses the "Calm under failure" trait. However, it adds complexity to the `sam.py` core.
*   **Trade-off:** Increases robustness at the cost of potential "false positives" where the network is just momentarily jittery.

### Option 2: Semantic Deduplication for `knowledge_log.json`
*   **Concept:** As the knowledge log grows, redundant entries (e.g., multiple entries on "Pydantic validation") waste space and confuse the Spaced Repetition engine. I could implement a routine that uses a simple embedding-based similarity check (or even just keyword-set intersection) to merge similar entries.
*   **Critique:** High long-term maintainability. It keeps the "brain" lean.
*   **Trade-off:** Requires adding a dependency or a simple vector-math utility to `bag/`.

**Selection:** Option 1 is more critical for operational stability. Given the "Agentic Orchestration" trend, my reliance on Gemini is increasing; I must ensure my core loop doesn't hang or thrash during API instability.

---

## Idea: Adaptive Circuit Breaker for Gemini API
Implement a `CircuitBreaker` class in `bag/` that monitors `ask_gemini` success/failure. If failures exceed 3 in a 5-minute window, the breaker trips, preventing further calls for 10 minutes and logging an alert to Dot.

## Why
My current `ask_gemini` has retry logic, but it lacks a "global" awareness of service health. If the API is down, I currently waste cycles and tokens on repeated failures. A circuit breaker allows me to "pause" and wait for recovery, preserving my state and preventing unnecessary log bloat.

## Implementation Steps
1.  **Create `bag/circuit_breaker.py`**: Define a class with `record_failure()`, `record_success()`, and `is_open()`.
2.  **Integrate into `sam.py`**: Update `ask_gemini` to check `is_open()` before attempting a call.
3.  **State Persistence**: Store the breaker state in `bag/` so it survives across cycle restarts.
4.  **Alerting**: If the breaker trips, trigger `_alert_dot` to inform the owner of the service outage.

## Risk
**Failure Mode:** The breaker trips due to a transient network issue, blocking me from performing critical self-repairs or state-saving.
**Mitigation:** Implement a "manual override" or a "force-reset" mechanism in `sam.py` that allows me to bypass the breaker if I detect that the failure was local (e.g., `TimeoutError` vs `ConnectionRefused`).

**Confidence Score:** 9/10