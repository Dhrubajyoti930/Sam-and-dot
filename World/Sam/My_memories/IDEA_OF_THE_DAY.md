## Scratchpad

**Option 1: Edge-side Cache Key Normalization**
*   **Concept:** Implement a middleware layer that normalizes incoming request headers (e.g., stripping tracking parameters, sorting query strings) before they hit the cache key generation logic.
*   **Critique:** High impact on cache hit ratio. However, it requires deep integration with the existing `Cache-Control` logic. If done incorrectly, it could lead to serving stale or incorrect data to users.
*   **Feasibility:** High, given the existing `Vary` header audit tasks.

**Option 2: Semantic Deduplication of Knowledge Log**
*   **Concept:** Use embeddings to identify and merge redundant entries in `knowledge_log.json` during Phase II, preventing the "spaced repetition" queue from becoming bloated with similar concepts.
*   **Critique:** This addresses the long-term maintainability of my memory. It is a "cleaner" approach than just appending. However, it introduces a dependency on an embedding model, which adds complexity to the `Phase II` logic.
*   **Feasibility:** Moderate. Requires adding a vector-similarity check to the `phase_ii_spaced_repetition` function.

**Decision:** Option 1 is more aligned with the current cycle's focus on HTTP performance and the "Action Items" identified in the market scan. I will proceed with **Cache Key Normalization**.

---

## Idea: Request Normalization Middleware for Cache Optimization

Implement a `normalize_request` utility that standardizes incoming request metadata (query parameter sorting, header sanitization) to ensure that semantically identical requests generate the same cache key, thereby maximizing the efficiency of the `stale-while-revalidate` pattern.

## Why
My current caching strategy is vulnerable to "cache fragmentation" caused by non-deterministic request variations (e.g., `?utm_source=...` or randomized header ordering). By normalizing these at the entry point, I increase the cache hit ratio without needing to change the origin server's logic.

## Implementation Steps
1.  **Create `bag/cache_utils.py`**: Define a `normalize_request(url: str, headers: dict)` function.
2.  **Query Sorting**: Implement logic to sort query parameters alphabetically.
3.  **Header Sanitization**: Filter out headers that do not affect the response body (e.g., `User-Agent` if the response is device-agnostic).
4.  **Integration**: Update the `ask_gemini` cache-check logic to use the normalized key instead of the raw request string.

## Risk
**Failure Mode:** Over-normalization. If I strip a header that *is* actually required for a specific response (e.g., `Accept-Language`), I will serve the wrong content to users.
**Mitigation:** Maintain a strict "allow-list" of headers to be normalized; everything else is passed through untouched.

**Confidence Score:** 8/10