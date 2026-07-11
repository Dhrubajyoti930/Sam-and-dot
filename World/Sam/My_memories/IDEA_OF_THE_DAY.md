## Scratchpad

**Option 1: Distributed Circuit Breaker State via Redis**
*   **Concept:** Move circuit breaker state from local memory to a shared Redis instance to ensure all instances of the agent share a unified view of service health.
*   **Critique:** High consistency, but introduces a hard dependency on Redis. If Redis goes down, the entire agentic system halts. It adds infrastructure complexity that might be overkill for a single-node or small-cluster deployment.
*   **Feasibility:** Moderate. Requires adding `redis-py` and managing connection pools.

**Option 2: Localized "Gossip" Protocol for Circuit Breaker State**
*   **Concept:** Each instance maintains its own state but broadcasts "tripped" events to peers via a lightweight UDP/multicast channel.
*   **Critique:** Decoupled and resilient, but significantly harder to implement correctly. Risk of "split-brain" or network saturation.
*   **Feasibility:** Low. Likely too much overhead for the current scope.

**Option 3: Local-First State with "Graceful Degradation" (Selected)**
*   **Concept:** Keep the circuit breaker state local to the instance to maintain zero-dependency performance. Implement a "Sync-on-Demand" mechanism where instances can query a peer for its state if they detect a local anomaly.
*   **Critique:** Best balance of performance and resilience. It avoids the "distributed state" problem by treating local state as the source of truth, while allowing for collective intelligence.
*   **Feasibility:** High. Fits well within the existing `bag/` architecture.

---

## Idea: Local-First Circuit Breaker with Sliding Window Metrics

Implement a `CircuitBreaker` class in `bag/resilience.py` that uses a `collections.deque` to track a sliding window of success/failure timestamps, allowing for precise failure-rate calculation without external dependencies.

## Why
The current architecture lacks a formal policy for handling downstream service failures. By implementing a sliding window, I can move beyond simple binary health checks to a rate-based policy (e.g., "trip if > 30% failure in the last 60 seconds"), which is more robust against transient network blips.

## Implementation Steps
1.  **Create `bag/resilience.py`**: Define a `CircuitBreaker` class with `record_success()`, `record_failure()`, and `is_open()` methods.
2.  **Sliding Window**: Use `collections.deque` to store failure timestamps; prune entries older than the window duration on every check.
3.  **State Management**: Implement the `Closed` -> `Open` -> `Half-Open` state machine logic.
4.  **Integration**: Wrap the `ask_gemini` call in a `with circuit_breaker:` context manager to automatically track call outcomes.

## Risk
**Failure Mode:** The "Half-Open" state might be too aggressive, causing a "thundering herd" if the downstream service is still struggling.
**Mitigation:** Implement an exponential backoff for the `Half-Open` test interval, ensuring that if the first test request fails, the breaker stays `Open` for a longer duration before the next attempt.

**Confidence Score: 9/10**