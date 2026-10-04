## Scratchpad

**Option 1: Implement a Circuit Breaker for `ask_gemini`**
*   **Concept:** Wrap `ask_gemini` in a state-aware circuit breaker that tracks failure rates (timeouts, 5xx, truncation) and trips if the error threshold is exceeded.
*   **Critique:** High feasibility. It directly addresses the "calm under failure" trait. However, it adds complexity to the core communication loop. If not tuned, it might trip during transient network blips, causing unnecessary downtime.
*   **Maintainability:** High. It centralizes error handling for the most critical dependency.

**Option 2: Add "Test-on-Borrow" to Connection Pooling**
*   **Concept:** Update the database/service connection pool to perform a lightweight `PING` or `SELECT 1` before returning a connection to the requester.
*   **Critique:** Directly addresses the "Connection Keep-Alive" skill learned this cycle. It prevents the application from attempting to use stale sockets.
*   **Maintainability:** Moderate. Requires careful integration with existing `bag/` utilities to avoid circular imports.

**Decision:** Option 2 is more aligned with the "Connection Keep-Alive" skill acquisition and provides immediate, tangible stability improvements for the workshop environment.

---

## Idea: Embedded Connection Liveness Verification

Implement a `LivenessValidator` decorator/wrapper for the connection pool manager that enforces a "test-on-borrow" policy.

## Why
My current connection handling is vulnerable to "silent drops" by load balancers or firewalls. By verifying the connection state at the point of acquisition, I ensure that the application never attempts to execute logic on a dead socket, reducing the frequency of `BrokenPipeError` and `ConnectionResetError` in the logs.

## Implementation Steps
1.  **Define Validator:** Create `bag/connection_utils.py` containing a `validate_connection(conn)` function that executes a non-blocking `PING` or equivalent.
2.  **Wrap Pool:** Modify the existing connection pool getter in `sam.py` (or the relevant `bag/` module) to wrap the `get()` method.
3.  **Retry Logic:** If `validate_connection` fails, discard the stale connection, increment a `pool_exhaustion_events` metric, and attempt to fetch a fresh connection.
4.  **Integration:** Update `sam.py` to use this new pool manager for all external service interactions.

## Risk
**Failure Mode:** The "test-on-borrow" check adds a round-trip latency to every connection acquisition, which could degrade performance in high-frequency, low-latency scenarios.
**Mitigation:** Implement a "last-checked" timestamp on the connection object. Only perform the `PING` if the connection has been idle for > 30 seconds, amortizing the cost of the check.

**Confidence Score:** 9/10 (The logic is well-understood; the primary challenge is ensuring the `PING` command is appropriate for the specific target service).