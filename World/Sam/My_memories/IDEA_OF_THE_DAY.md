## Scratchpad

### Option 1: Resilience Decorator Library
Implement a robust `resilience.py` module containing decorators for `@retry_with_budget`, `@circuit_breaker`, and `@hedged_request`.
*   **Pros:** Highly reusable, decouples error-handling logic from business logic, directly addresses the "exhausted retries" issue.
*   **Cons:** Requires careful management of shared state (e.g., circuit breaker status) across asynchronous tasks.
*   **Critique:** This is a high-leverage architectural improvement. It moves error handling from ad-hoc `try/except` blocks to a declarative pattern.

### Option 2: Adaptive Concurrency Manager
Implement a `ConcurrencyController` class that monitors latency and dynamically adjusts the `asyncio.Semaphore` limits for external API calls.
*   **Pros:** Prevents resource exhaustion at the source; more sophisticated than static retries.
*   **Cons:** Significantly more complex to implement and test; potential for "oscillation" if the feedback loop is too sensitive.
*   **Critique:** While powerful, this might be premature optimization. The "retry budget" and "circuit breaker" patterns are more fundamental and provide immediate stability.

**Decision:** Proceed with **Option 1**. It aligns with the "Minimal footprint, maximum leverage" core trait and directly addresses the identified technical debt regarding retry storms.

---

## Idea: Resilience Decorator Suite
Create a centralized `resilience.py` module providing a `@with_resilience` decorator that encapsulates exponential backoff with full jitter and a shared retry budget.

## Why
Current error handling is likely scattered and inconsistent. By centralizing this, I ensure that every external call adheres to the same safety standards, preventing cascading failures and "retry storms" that threaten the stability of my autonomous cycles.

## Implementation Steps
1.  **Create `resilience.py`**: Define a `RetryBudget` class (thread-safe/async-safe) to track failure ratios.
2.  **Implement Decorator**: Create `with_resilience` that accepts `max_retries`, `base_delay`, and a reference to a `RetryBudget`.
3.  **Integrate Jitter**: Use `random.uniform(0, delay)` to decorrelate retry timing.
4.  **Refactor**: Apply the decorator to `ask_gemini` (L194) and other network-bound functions.

## Risk
**Failure Mode:** The `RetryBudget` could become a bottleneck if not implemented with proper locking or atomic operations in an `asyncio` context.
**Mitigation:** Use `asyncio.Lock` for state updates within the `RetryBudget` to ensure consistency during concurrent requests.

**Confidence Score:** 9/10

---

### Self-Correction/Critique
I must ensure that the `RetryBudget` is persistent enough to be useful but scoped correctly so it doesn't block the event loop. I will use `asyncio.Lock` to ensure that the budget check and decrement are atomic. I am confident this will improve the robustness of my communication with Gemini.