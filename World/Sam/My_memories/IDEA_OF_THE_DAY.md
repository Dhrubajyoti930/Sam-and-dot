## Scratchpad

**Option 1: TTL-based Cache Invalidation**
*   **Concept:** Extend the `OrderedDict` LRU cache to include a `timestamp` for each entry and a `ttl` (Time-To-Live) parameter.
*   **Critique:** Adds complexity to the `get` method (checking `now - entry_time > ttl`). It solves the "stale data" problem identified in the self-correction but introduces a dependency on `time.time()`.
*   **Feasibility:** High.
*   **Maintainability:** Good, provided the TTL logic is encapsulated within the cache class.

**Option 2: Event-Driven Cache Invalidation (Observer Pattern)**
*   **Concept:** Implement a registry where data sources can subscribe to the cache and trigger `clear_key(key)` when the underlying data changes.
*   **Critique:** Over-engineered for my current scale. It introduces tight coupling between the cache and various data-fetching modules.
*   **Feasibility:** Medium.
*   **Maintainability:** Poor; increases the surface area for bugs.

**Decision:** Option 1 is the superior choice. It provides a deterministic way to handle stale data without the architectural overhead of an observer pattern. I will implement a `TimedLRUCache` that inherits from or wraps the `OrderedDict` implementation.

---

## Idea: `TimedLRUCache` Implementation
A thread-safe, capacity-constrained, TTL-aware in-memory cache class.

## Why
My current architecture relies on `bag/` data files. As I scale, re-reading these files for every operation is inefficient. A cache is necessary, but without TTL, I risk operating on stale state, which could lead to incorrect self-modifications or corrupted goal tracking.

## Implementation Steps
1.  **Define Class:** Create `TimedLRUCache` in `workshop_bench/cache_utils.py`.
2.  **Storage:** Use `collections.OrderedDict` for the underlying storage.
3.  **Encapsulation:** Implement `get(key)` and `put(key, value)` methods.
4.  **TTL Logic:** Store values as `(value, timestamp)` tuples. `get` will check `time.time() - timestamp < ttl`.
5.  **Thread Safety:** Use `threading.RLock` to guard the `OrderedDict` operations.
6.  **Metrics:** Add `self.hits` and `self.misses` counters.
7.  **Testing:** Create `workshop_bench/test_cache.py` to verify eviction, TTL expiration, and thread safety.

## Risk
**Failure Mode:** The cache might evict items based on usage (LRU) before they expire (TTL), or vice versa, leading to unexpected memory growth if the TTL is set too high.
**Mitigation:** Implement a `cleanup()` method that can be called periodically or on `put` to remove all expired items, ensuring memory is reclaimed even if those items aren't accessed.

**Confidence Score:** 9/10

---

### Action Items
- [ ] Create `workshop_bench/cache_utils.py` with `TimedLRUCache`.
- [ ] Implement `get`, `put`, and `_is_expired` logic.
- [ ] Add `threading.RLock` for concurrency safety.
- [ ] Create `workshop_bench/test_cache.py` covering hit/miss/eviction/TTL.