## Scratchpad

**Option 1: Distributed Rate-Limit Synchronization (Redis-backed)**
*   **Concept:** Replace local rate-limit tracking with a centralized Redis store to handle multi-instance quota management.
*   **Critique:** High architectural overhead. Requires managing a Redis dependency and connection pooling within `sam.py`. While robust for horizontal scaling, it introduces a single point of failure and adds significant complexity to the `ask_gemini` flow.
*   **Feasibility:** Moderate.
*   **Maintainability:** Low (adds infrastructure dependency).

**Option 2: Adaptive Backoff Middleware (Local-first)**
*   **Concept:** Implement a decorator-based middleware for `ask_gemini` that wraps calls in a `tenacity`-like retry loop, specifically parsing `Retry-After` and `RateLimit-Reset` headers to dynamically adjust `_CALL_DELAY`.
*   **Critique:** Aligns perfectly with the "Technical Summary" learned this cycle. It improves resilience without external dependencies. It treats rate limits as a feedback loop rather than a static constant.
*   **Feasibility:** High.
*   **Maintainability:** High (encapsulated within `sam.py` or `bag/`).

**Selection:** Option 2. It directly addresses the "Action Items" identified in the technical summary and improves the reliability of the `ask_gemini` core service.

---

## Idea: Adaptive Rate-Limit Middleware for `ask_gemini`

Implement a `RateLimitHandler` class that tracks API state and dynamically adjusts `_CALL_DELAY` based on real-time HTTP response headers (`RateLimit-Remaining`, `Retry-After`).

## Why
Currently, `_CALL_DELAY` is static. This is inefficient: it either wastes time (if the quota is high) or risks 429 errors (if the quota is low). By making the delay adaptive, I can maximize throughput during high-quota windows and gracefully throttle during congestion, fulfilling the "Resilience Patterns" requirement.

## Implementation Steps
1.  **Define `RateLimitState`:** A simple class to store `reset_time` and `remaining_quota`.
2.  **Update `ask_gemini`:** Wrap the `CLIENT.models.generate_content` call in a try-except block that catches `429` status codes.
3.  **Header Parsing:** Extract `Retry-After` or `RateLimit-Reset` from the exception response.
4.  **Dynamic Adjustment:** Update `_CALL_DELAY` globally based on the parsed reset time, adding a jitter factor ($random(0.5, 1.5) \times \text{delay}$).
5.  **Integration:** Inject this logic into the `ask_gemini` flow before the `_sleep()` call.

## Risk
**Failure Mode:** If the API provider changes header naming conventions or stops sending them, the adaptive logic could default to an overly aggressive or overly conservative delay.
**Mitigation:** Implement a "sanity bound" for `_CALL_DELAY` (e.g., never lower than 0.5s, never higher than 60s) to ensure the system remains functional even if the adaptive logic fails.

**Confidence Score:** 9/10