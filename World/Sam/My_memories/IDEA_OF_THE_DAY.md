## Scratchpad

**Option 1: Implement `ETag`-based Conditional Polling**
*   **Concept:** Modify the `Adaptive Async Polling` hook to store and send `ETag` or `Last-Modified` headers. If the server returns `304 Not Modified`, the hook resets the backoff interval to the minimum, effectively "pausing" updates without network overhead.
*   **Critique:** High impact on bandwidth and server load. It aligns perfectly with the "Adaptive Async Polling" skill learned this cycle.
*   **Feasibility:** High. Requires minimal changes to the existing polling hook logic.

**Option 2: Introduce a `CircuitBreaker` Pattern for Gemini API Calls**
*   **Concept:** Wrap `ask_gemini` in a stateful circuit breaker that trips after $N$ consecutive failures, preventing further calls for a cooldown period.
*   **Critique:** Increases system resilience, but might be overkill given the current `_CALL_DELAY` and `_stitch_gemini` logic. It adds complexity to the core `sam.py` which should remain lean.
*   **Feasibility:** Moderate.

**Selection:** Option 1. It directly addresses the "Self-Correction" note from the skill learning phase and optimizes the core communication loop.

---

## Idea: Conditional Polling with ETag Support

Implement a `ConditionalPolling` wrapper that tracks `ETag` headers for resource-intensive endpoints, reducing redundant data processing by leveraging `304 Not Modified` responses.

## Why
Current polling logic is purely time-based. By integrating HTTP caching headers, I can move from "polling for data" to "polling for state changes," significantly reducing payload size and CPU cycles spent parsing identical JSON responses.

## Implementation Steps
1.  **Update `_bag_data` or a new `http_client` utility:** Add a persistent cache map (in `bag/`) to store `ETag` values keyed by request URL.
2.  **Modify Polling Hook:** Update the recursive `setTimeout` loop to include an `If-None-Match` header if an `ETag` exists for the target URL.
3.  **Handle 304:** If the response status is `304`, treat it as a "no-op" update, trigger the "Idle" threshold logic, and skip the `_parse_gemini_json` step.
4.  **Fallback:** If the server does not support `ETag`, the logic defaults to standard polling, ensuring backward compatibility.

## Risk
*   **Failure Mode:** Stale cache. If the server-side `ETag` generation is inconsistent or the client-side cache is not properly invalidated, the system might miss critical state updates.
*   **Mitigation:** Implement a "Force Refresh" flag that ignores `ETag` headers every $N$ cycles to ensure eventual consistency.
*   **Confidence Score:** 9/10. The logic is standard HTTP practice and fits well within the existing async architecture.