## Scratchpad

### Option 1: Virtual Proxy for `bag/` resource loading
*   **Concept:** Implement a `VirtualProxy` class in `sam.py` to wrap heavy `bag/` data files (e.g., large JSON knowledge logs or historical logs). These are currently loaded eagerly.
*   **Critique:** 
    *   *Pros:* Reduces memory footprint during startup; improves responsiveness.
    *   *Cons:* Adds complexity to `_bag_data` resolution; potential for race conditions if multiple threads access the proxy during initialization.
    *   *Feasibility:* High. Python’s `__getattr__` makes this transparent.

### Option 2: Caching Proxy for External API Service Layer
*   **Concept:** Introduce a `CachingProxy` to wrap `ask_gemini` calls that are repetitive or non-critical (e.g., secondary metadata lookups).
*   **Critique:**
    *   *Pros:* Significant reduction in API latency and cost; respects RPM limits more effectively.
    *   *Cons:* Cache invalidation is notoriously difficult. If the proxy caches stale data, the system state becomes inconsistent.
    *   *Feasibility:* Moderate. Requires a robust TTL or version-based invalidation strategy.

### Selection: Option 1 (Virtual Proxy)
I choose Option 1. It aligns with my current skill acquisition (Proxy Pattern) and directly addresses the "memory bloat" concern I identified in my self-correction. It is a surgical, low-risk refactor that improves the long-term maintainability of my core services.

---

## Idea: Virtual Proxy for `bag/` Data Access
Implement a `LazyBagProxy` class that defers the loading of large `bag/` files until the first attribute access, replacing the current eager `json.load()` calls in `load_experiences` and similar functions.

## Why
My current architecture loads entire JSON files into memory even when only a subset of data is needed. As my `experiences.json` and `knowledge_log.json` grow, this creates unnecessary memory pressure. A Virtual Proxy allows me to maintain the existing API while optimizing resource lifecycle management.

## Implementation Steps
1.  Define `LazyBagProxy` in `sam.py` using `__getattr__` to intercept access to the underlying data.
2.  Refactor `load_experiences` to return a `LazyBagProxy` instance instead of the raw list.
3.  Implement a `_load()` method within the proxy that performs the actual `json.load()` only upon the first interaction.
4.  Ensure the proxy clears the reference to the real object if the system signals a memory-pressure event (optional, but good for robustness).

## Risk
*   **Failure Mode:** The proxy might hold a strong reference to the loaded data indefinitely, effectively negating the memory benefits if the data is accessed frequently.
*   **Mitigation:** Implement a `reset()` method on the proxy to nullify the internal cache, allowing the garbage collector to reclaim memory after a specific operation completes.
*   **Confidence Score:** 9/10. The pattern is well-understood, and the impact on existing code is minimal due to the transparent nature of `__getattr__`.