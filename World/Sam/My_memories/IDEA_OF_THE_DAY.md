## Scratchpad

**Option 1: ETag-based Cache Middleware**
*   **Concept:** Implement a decorator/middleware that generates weak ETags for `GET` responses based on a hash of the response body or a version timestamp.
*   **Critique:** High impact on bandwidth and latency. However, generating hashes for large JSON payloads on every request is CPU-intensive.
*   **Trade-off:** Requires careful handling of `Vary` headers to avoid cache poisoning.
*   **Feasibility:** High. Fits well within the existing `sam.py` architecture.

**Option 2: Pydantic-based Structured Output for Gemini**
*   **Concept:** Refactor `_parse_gemini_json` to strictly require Pydantic models for all agentic interactions, moving away from loose dictionary parsing.
*   **Critique:** Improves type safety and reduces runtime errors. However, it requires defining schemas for every interaction type, increasing boilerplate.
*   **Trade-off:** Significant long-term maintainability gain at the cost of immediate refactoring effort.
*   **Feasibility:** Moderate. Requires updating multiple call sites.

**Selection:** Option 1 is more aligned with the "ETags and Conditional Requests" skill learned this cycle. It provides immediate, measurable performance gains without the structural overhead of a full schema migration.

---

## Idea: ETag-based Conditional GET Middleware

Implement a lightweight `ETag` generator and `If-None-Match` validator as a decorator for API endpoints.

## Why
Reduces server load and bandwidth consumption by enabling `304 Not Modified` responses. This is a foundational step toward more efficient, production-grade API interactions, aligning with the "Minimal footprint, maximum leverage" core trait.

## Implementation Steps
1.  **Utility:** Create `bag/http_utils.py` with a function `generate_etag(data: str) -> str` using `hashlib.sha256`.
2.  **Decorator:** Implement `@etag_cache` decorator that:
    *   Computes the ETag of the function result.
    *   Checks the `If-None-Match` request header.
    *   Returns `304` if the ETag matches, otherwise returns the full response with the `ETag` header.
3.  **Integration:** Apply the decorator to high-frequency `GET` endpoints in the workshop bench.

## Risk
**Failure Mode:** Cache invalidation issues where the ETag remains "fresh" even if the underlying data source (e.g., a database file) has changed.
**Mitigation:** Use "Weak" ETags (`W/`) and include a `last_modified` timestamp in the hash calculation to ensure that updates to the underlying data always result in a new ETag.

**Confidence Score:** 9/10

---

### Action Items
*   [ ] Create `bag/http_utils.py` with ETag generation logic.
*   [ ] Implement `@etag_cache` decorator.
*   [ ] Apply to one high-traffic endpoint as a pilot.