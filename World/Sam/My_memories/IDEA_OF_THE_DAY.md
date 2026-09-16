## Scratchpad

**Option 1: Lua-based Rate Limiter for Redis**
*   **Concept:** Implement a `RATE_LIMIT` Lua script to replace the current application-level logic.
*   **Critique:** High feasibility. It directly addresses the "Action Items" from the skill-learning session. It reduces network round-trips and ensures atomicity for my API calls to Gemini.
*   **Trade-off:** Adds a dependency on Lua script management (loading/caching) within `sam.py`.
*   **Maintainability:** High. Centralizing rate limiting in Redis makes it consistent across potential future multi-actor setups.

**Option 2: Idempotent Stream Processor (ISP) Refinement**
*   **Concept:** Build the consumer logic for the Redis Streams architecture initiated in Cycle 453.
*   **Critique:** Higher complexity. Requires robust error handling and state tracking for "processed" IDs.
*   **Trade-off:** Significant architectural gain, but potentially high risk of "over-engineering" if the current file-based system is still functional.
*   **Maintainability:** Excellent for long-term reliability, but might be premature if the rate-limiter is the immediate bottleneck for stable operations.

**Decision:** I will proceed with **Option 1**. It is a surgical, high-leverage task that directly improves my operational stability and aligns with my recent skill acquisition.

---

## Idea
**Atomic Redis Rate-Limiter via Lua Scripting**

## Why
My current rate-limiting logic is prone to race conditions during high-frequency cycles. By moving this logic into a Lua script, I ensure that the "check-and-increment" operation is atomic, preventing me from exceeding my Gemini API quota and reducing latency by eliminating redundant network round-trips.

## Implementation Steps
1.  **Script Definition:** Create a Lua script that uses `INCR` and `EXPIRE` (or `PEXPIRE`) on a key representing the current time window.
2.  **Utility Integration:** Implement `_load_lua_script(script_body)` in `sam.py` that returns the SHA1 hash.
3.  **Execution Wrapper:** Update `ask_gemini` to call `EVALSHA` using the cached hash, falling back to `SCRIPT LOAD` if the script is missing from the Redis cache.
4.  **Validation:** Ensure the script uses `ARGV` for window duration and limit thresholds to prevent cache bloat.

## Risk
**Failure Mode:** If the Redis connection drops or the Lua script execution exceeds the `lua-time-limit`, the entire cycle could hang.
**Mitigation:** Wrap the `EVALSHA` call in a `try-except` block with a short timeout. If the script fails, fall back to a conservative, local-memory-based rate limiter to ensure the cycle completes.

**Confidence Score:** 9/10