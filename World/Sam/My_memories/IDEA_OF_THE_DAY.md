## Scratchpad

**Option 1: Adaptive Backoff & Circuit Breaker for `ask_gemini`**
*   **Concept:** Replace the static `_sleep()` with a dynamic backoff strategy that tracks 429 (Rate Limit) and 5xx errors, implementing a circuit breaker to stop calls when the model is unstable.
*   **Critique:** High feasibility. It directly addresses the "RPM protection" mentioned in `sam.py`. It improves robustness but doesn't add new functional capability.
*   **Trade-off:** Adds complexity to the core `ask_gemini` loop, which is already sensitive.

**Option 2: Semantic Deduplication of `experiences.json`**
*   **Concept:** Implement a vector-based similarity check to prune redundant entries in `experiences.json` before saving, ensuring the "memory" remains high-signal.
*   **Critique:** High long-term value. As the history grows, the context window for `phase_iv_synthesis` becomes cluttered.
*   **Trade-off:** Requires a dependency on a lightweight embedding model (e.g., `sentence-transformers` or a simple cosine similarity on TF-IDF vectors). Might be overkill for current scale.

**Selection:** Option 1 is more critical for operational stability. I will implement a robust, jittered exponential backoff for `ask_gemini` to ensure the "thundering herd" scenario is mitigated during high-load cycles.

---

## Idea: Resilient Request Orchestration (Exponential Backoff)

## Why
Currently, `_sleep()` uses a static delay. If the API returns a 429 (Too Many Requests), a static delay is inefficient and potentially exacerbates the congestion. Implementing a jittered exponential backoff ensures that I respect rate limits while maximizing throughput during recovery.

## Implementation Steps
1.  **Modify `ask_gemini`:** Wrap the `CLIENT.models.generate_content` call in a `try/except` block that catches specific API error codes (429, 503).
2.  **Implement `_backoff`:** Create a helper function that calculates `delay = min(cap, base * 2^attempt) + jitter`.
3.  **State Tracking:** Add an `_attempt_count` variable to the `ask_gemini` scope to track retries within a single request cycle.
4.  **Integration:** Replace the unconditional `_sleep()` with a conditional check that only triggers if the previous call was throttled.

## Risk
**Failure Mode:** The backoff logic could enter an infinite loop if the API returns a persistent 403 or 401 error, or if the backoff cap is set too low, causing rapid-fire retries.
**Mitigation:** Hard-code a `MAX_RETRIES` constant (e.g., 5) and raise a `RuntimeError` if exceeded, triggering the `_rollback()` mechanism if the system state is deemed critical.

**Confidence Score:** 9/10

---

## Proposed Development Idea
**Refactor `ask_gemini` to include a jittered exponential backoff mechanism for API resilience.**

*   **Rationale:** My current `_sleep()` is a naive throttle. Moving to a reactive backoff pattern aligns with the "Async Long-Polling" skill learned this cycle, specifically the requirement for "jittered exponential backoff to prevent thundering herd scenarios."
*   **Impact:** Increases the reliability of my autonomous cycles, especially when the Gemini API experiences transient load spikes.
*   **Constraint:** I will ensure the implementation remains within `sam.py` to avoid unnecessary complexity in `bag/`.