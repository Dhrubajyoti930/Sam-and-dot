## Scratchpad

**Option 1: Adaptive Token-Bucket Middleware**
*   **Concept:** Implement a `TokenBucket` class in `bag/middleware.py` that tracks `TPM` (Tokens Per Minute) and `RPM` (Requests Per Minute) using Redis.
*   **Critique:** High impact on reliability. It directly addresses the "thundering herd" and API cost issues.
*   **Trade-off:** Adds complexity to the `ask_gemini` call stack. Requires careful handling of Redis connectivity failures (must fail-open to avoid blocking all operations).
*   **Feasibility:** High. The logic is well-defined in the cycle's technical summary.

**Option 2: Semantic Cache Interceptor**
*   **Concept:** Before calling `ask_gemini`, compute an embedding of the prompt and query the vector store for a high-similarity match.
*   **Critique:** Significant latency and cost reduction. However, it risks serving stale or contextually inappropriate responses if the similarity threshold is too loose.
*   **Trade-off:** Requires maintaining an embedding model (e.g., `sentence-transformers`) within the workshop environment.
*   **Feasibility:** Moderate. Requires setting up the vector search pipeline.

**Selection:** Option 1 is more critical for immediate stability and aligns with the "API Rate Limiting" skill learned this cycle. I will proceed with the Redis-backed Token Bucket.

---

## Idea: Redis-Backed Token Bucket Middleware

Implement a `TokenBucket` rate-limiter that tracks both `RPM` and `TPM` (Tokens Per Minute) in Redis, wrapping the `ask_gemini` function to enforce proactive throttling.

## Why
Current rate limiting is reactive (handling `429` errors). Proactive limiting based on token consumption prevents API provider bans, reduces costs by shedding low-priority tasks, and stabilizes the system under high load.

## Implementation Steps
1.  **Create `bag/rate_limiter.py`:** Define a `TokenBucket` class using `redis-py` with Lua scripts for atomic `check-and-decrement` operations.
2.  **Update `sam.py`:** Modify `ask_gemini` to instantiate/call the `TokenBucket` before dispatching the request.
3.  **Token Estimation:** Add a helper function to estimate token count (e.g., `len(prompt) / 4`) to decrement the bucket before the call.
4.  **Backoff Integration:** Implement exponential backoff with jitter in the `ask_gemini` retry loop if the bucket is empty.

## Risk
**Failure Mode:** Redis connection timeout or unavailability could halt all AI operations.
**Mitigation:** Implement a "fail-open" decorator: if the Redis client raises a `ConnectionError`, log the warning and proceed with the request (defaulting to provider-side rate limiting).

**Confidence Score:** 9/10