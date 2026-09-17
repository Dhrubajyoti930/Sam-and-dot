## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a state-aware circuit breaker that tracks failure rates (timeouts, 5xx, truncation loops). If the error rate exceeds a threshold, the system enters an "Open" state, forcing a cooldown period or switching to a secondary, lower-latency model (e.g., a local SLM).
*   **Critique:** High maintainability and robustness. It directly addresses the "calm under failure" trait. However, it adds complexity to the `sam.py` core and requires managing state across cycles.
*   **Feasibility:** High.

**Option 2: Semantic Deduplication of Knowledge Log.**
*   **Concept:** Use the existing `knowledge_log.json` to perform a vector-based similarity check before adding new entries. If a new skill is semantically redundant (e.g., 90%+ cosine similarity to an existing entry), merge the new summary into the old one rather than appending.
*   **Critique:** Keeps the knowledge base lean and improves the quality of Phase II (Spaced Repetition). It prevents the log from becoming a "junk drawer."
*   **Feasibility:** Medium. Requires integrating a lightweight vector embedding (e.g., `sentence-transformers`) or a simple Jaccard similarity check on keywords.

**Decision:** Option 1 is more critical for long-term stability. As I scale, the fragility of external API calls is my biggest bottleneck. I will prioritize the Circuit Breaker.

---

## Idea: Circuit Breaker for API Resilience

## Why
My current `ask_gemini` implementation relies on simple retries. If the API is experiencing a sustained outage or rate-limit degradation, I waste cycles and tokens on doomed calls. A circuit breaker will allow me to fail fast, preserve resources, and potentially switch to a "safe mode" (e.g., local fallback or skipping non-critical tasks) when the primary provider is unstable.

## Implementation Steps
1.  **State Tracking:** Add `circuit_state.json` to `bag/` to persist the breaker status (CLOSED, OPEN, HALF-OPEN) and failure counts.
2.  **Wrapper Logic:** Modify `ask_gemini` to check `circuit_state.json` before execution.
3.  **Transition Logic:** 
    *   If `CLOSED` and failure threshold reached: set to `OPEN` with a timestamp.
    *   If `OPEN` and cooldown expired: set to `HALF-OPEN` to test the connection.
    *   If `HALF-OPEN` and success: reset to `CLOSED`.
4.  **Integration:** Update `_sleep()` and `ask_gemini` to respect the breaker state.

## Risk
**Failure Mode:** The circuit breaker enters an `OPEN` state prematurely due to a transient network blip, causing me to skip critical tasks for the duration of the cooldown.
**Mitigation:** Implement a "sliding window" failure counter rather than a simple count, and ensure that `Phase VII` (State Saving) can bypass the breaker if the task is deemed "critical" (e.g., saving state).

**Confidence Score:** 8/10. The logic is standard, but the state persistence across cycles requires careful handling of the `bag/` file system.