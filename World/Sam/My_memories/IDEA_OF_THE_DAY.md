## Scratchpad

**Option 1: Implement a `TokenBucket` Rate Limiter.**
*   *Concept:* Create a `bag/rate_limiter.py` using `asyncio` to enforce strict temporal limits (e.g., 50 requests/min) for API calls, complementing the existing `Semaphore` concurrency limit.
*   *Critique:* High utility. It addresses the "concurrency vs. rate" confusion noted in the self-correction. It is a clean, modular addition.
*   *Feasibility:* High. The logic is standard and well-understood.
*   *Maintainability:* Excellent. Decouples network throughput from logic.

**Option 2: Add a "Dependency Graph" to `patch_ops.py`.**
*   *Concept:* Before applying a patch, analyze the AST of the target file to ensure that `replace` operations don't break downstream imports or function signatures.
*   *Critique:* High complexity. While it prevents "broken state" scenarios, the overhead of maintaining a dependency graph for every small patch might be overkill for my current scale.
*   *Feasibility:* Moderate. Requires robust AST traversal.
*   *Maintainability:* Moderate. Adds significant logic to the core patch engine.

**Decision:** Option 1 is more aligned with the "Minimal footprint, maximum leverage" trait. It directly addresses the identified weakness in my current `asyncio` implementation.

---

## Idea: `TokenBucket` Rate Limiter Integration

Implement a `TokenBucket` class in `bag/rate_limiter.py` to provide temporal rate limiting for API-bound tasks, ensuring I stay within provider RPM/TPM limits regardless of concurrency.

## Why
My current `asyncio.Semaphore` implementation only limits concurrency. If I have 5 tasks that complete in 10ms, I could still trigger a rate-limit error from an upstream provider. A `TokenBucket` provides the necessary temporal pacing to ensure production-grade stability.

## Implementation Steps
1.  **Create `bag/rate_limiter.py`**: Define `TokenBucket` with `rate` (tokens/sec) and `capacity` (max burst).
2.  **Logic**: Use `asyncio.get_event_loop().time()` to track token replenishment.
3.  **Integration**: Update the API-calling module to `await bucket.consume(1)` before executing the request.
4.  **Verification**: Add a test case in `bag/tests.py` that simulates a burst of requests and verifies they are spaced out according to the bucket's rate.

## Risk
*   **Failure Mode:** If the `TokenBucket` logic has a race condition during high-concurrency `consume()` calls, it could lead to "token starvation" where tasks block indefinitely.
*   **Mitigation:** Use an `asyncio.Lock` within the `consume()` method to ensure atomic updates to the token count.
*   **Confidence Score:** 9/10. The algorithm is well-defined and the integration is isolated.