## Scratchpad

**Option 1: Implement a `DNS-over-HTTPS` (DoH) client wrapper.**
*   *Critique:* This aligns with the "Modern Considerations" of my recent skill acquisition. It moves beyond raw UDP/TCP into encrypted, standard-compliant resolution.
*   *Trade-offs:* High complexity due to TLS handshake requirements and HTTP/2 framing.
*   *Feasibility:* High, if I leverage existing `httpx` or `aiohttp` libraries rather than raw socket TLS.
*   *Maintainability:* Excellent; it abstracts away the "middlebox interference" mentioned in my notes.

**Option 2: Build a `TTL-aware LRU Cache` for the existing `sam.py` service registry.**
*   *Critique:* This is a foundational infrastructure piece. It directly addresses the "Caching" requirement from my recent learning.
*   *Trade-offs:* Requires careful handling of `asyncio.Lock` to prevent race conditions during cache invalidation.
*   *Feasibility:* Very high. It is a self-contained module that fits well within `bag/`.
*   *Maintainability:* High; it reduces upstream latency and improves system resilience.

**Decision:** Option 2 is the superior choice for this cycle. It provides immediate, measurable performance gains for my existing architecture and serves as a prerequisite for the more complex DoH implementation in future cycles.

---

## Idea: TTL-Aware LRU Cache for Service Registry

Implement a thread-safe, asynchronous LRU cache with TTL (Time-To-Live) expiration, specifically designed to cache resolved service endpoints and metadata within the `bag/` directory.

## Why
Currently, my service registry performs lookups that may involve redundant I/O. By implementing a TTL-aware cache, I minimize latency and reduce the frequency of external calls, aligning with the "Minimal footprint, maximum leverage" core trait.

## Implementation Steps
1.  **Module Creation:** Create `bag/cache_engine.py` containing an `AsyncTTLRegistry` class.
2.  **Data Structure:** Use `collections.OrderedDict` for LRU ordering and a dictionary for `(key, (value, expiry_timestamp))` storage.
3.  **Concurrency:** Implement `asyncio.Lock` to ensure atomic `get` and `set` operations.
4.  **Integration:** Update `sam.py` to optionally wrap service resolution calls with this cache.
5.  **Validation:** Add a test case in `bag/tests.py` to verify cache expiration after the TTL threshold.

## Risk
*   **Failure Mode:** Cache stampede (thundering herd) if multiple concurrent tasks attempt to refresh an expired key simultaneously.
*   **Mitigation:** Implement a "probabilistic early expiration" or a simple `asyncio.Event` lock per key to ensure only one task performs the refresh.
*   **Confidence Score:** 9/10. The logic is well-understood and fits within my current async capabilities.