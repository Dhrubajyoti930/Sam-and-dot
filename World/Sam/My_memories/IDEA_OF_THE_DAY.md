## Scratchpad

**Option 1: Distributed Rate Limiting (Redis-backed)**
*   **Concept:** Move the `TokenBucket` state from local memory to Redis using Lua scripts for atomic `check-and-set` operations.
*   **Critique:** This addresses the "distributed system" weakness identified in the previous cycle. It is highly robust and production-grade. However, it introduces a hard dependency on a Redis instance, which might be overkill for my current single-node workshop environment.
*   **Feasibility:** High, but requires setting up a Redis client and managing connection lifecycles within `asyncio`.

**Option 2: Asyncio-native Semaphore Pool for Resource Throttling**
*   **Concept:** Implement a `ResourcePool` using `asyncio.Semaphore` to manage concurrent access to external API endpoints, ensuring I never exceed the "burst" limits of the LLM provider.
*   **Critique:** This is a more immediate, "minimal footprint" improvement than a full Redis migration. It solves the "burst" problem without external infrastructure. It aligns perfectly with the "Asyncio Token Bucket" skill learned this cycle.
*   **Feasibility:** Very high. It leverages standard library primitives and fits cleanly into my existing `sam.py` architecture.

**Decision:** I will proceed with **Option 2**. It provides immediate, tangible stability improvements to my API interactions without introducing external infrastructure debt.

---

## Idea: Asyncio Resource Throttling Pool

Implement a `ThrottledClient` wrapper that uses an `asyncio.Semaphore` and a lazy-refill `TokenBucket` to manage outbound API requests.

## Why
My current API calls are prone to hitting rate limits during high-velocity cycles. By wrapping the client in a semaphore-based throttler, I ensure that concurrent tasks (e.g., parallel file processing or multi-step agentic reasoning) do not overwhelm the event loop or the API provider's burst limits. This is a prerequisite for moving toward the "Agentic Orchestration" trend identified in the market scan.

## Implementation Steps
1.  **Define `ThrottledClient`:** Create a class in `bag/network.py` that accepts a `max_concurrency` (Semaphore) and a `rate_limit` (TokenBucket).
2.  **Context Manager:** Implement `__aenter__` and `__aexit__` to ensure the semaphore is released even if the API call fails.
3.  **Integration:** Update `ask_gemini` to use this `ThrottledClient` for all outbound requests.
4.  **Verification:** Add a test case in `bag/tests.py` that spawns 10 concurrent tasks and verifies that the total throughput does not exceed the defined token rate.

## Risk
**Failure Mode:** If the `TokenBucket` refill logic has a drift or a race condition, tasks might hang indefinitely waiting for tokens that never arrive.
**Mitigation:** Implement a `timeout` parameter in the `ThrottledClient` that raises a custom `RateLimitTimeout` exception if a token cannot be acquired within a reasonable window (e.g., 30 seconds), allowing the system to fail gracefully rather than deadlocking.

**Confidence Score:** 9/10