## Scratchpad

**Option 1: Type-Safe State Machine for `run_cycle`**
*   **Concept:** Replace the current procedural `run_cycle` with a formal state machine using Python `Enum` and `match` statements.
*   **Critique:** This aligns with the Curry-Howard goal of making illegal states unrepresentable. It would replace the implicit flow with an explicit, verifiable transition graph.
*   **Trade-off:** High refactoring cost for `sam.py`. Risk of breaking the existing `phase_x` orchestration logic.
*   **Feasibility:** High, but requires careful mapping of current dependencies.

**Option 2: Semantic Cache TTL & Eviction Policy**
*   **Concept:** Implement a time-to-live (TTL) and LRU eviction policy for the semantic cache in `bag/semantic_cache.py`.
*   **Critique:** Currently, the cache grows monotonically. As I evolve, old "wisdom" may become stale or contradictory. A TTL ensures I am not relying on outdated reasoning patterns.
*   **Trade-off:** Requires adding metadata (timestamps) to the cache entries.
*   **Feasibility:** Very high. It is a targeted, low-risk improvement that directly supports "Disciplined curiosity."

**Decision:** Option 2 is superior for this cycle. It directly addresses the "long-term maintainability" requirement by preventing cache bloat and stale reasoning, while being a surgical change that respects the "minimal footprint" principle.

---

## Idea: Temporal Cache Invalidation (TTL)
Implement a 14-cycle TTL for semantic cache entries to ensure that my "wisdom" remains aligned with my current architectural state and evolving personality.

## Why
My semantic cache currently acts as a permanent memory. If my internal logic or the ecosystem shifts (as identified in the market scan), stale cache hits can lead to suboptimal or outdated decision-making. A TTL forces a "refresh" of reasoning patterns, ensuring I remain adaptive.

## Implementation Steps
1.  Modify `bag/semantic_cache.py` to include a `timestamp` field in the JSON cache schema.
2.  Update `check_cache` to compare `current_cycle - entry_cycle` against a `TTL_THRESHOLD` (14).
3.  If `expired`, trigger a cache miss to force a fresh Gemini call.
4.  Update `update_cache` to store the current `cycle` number with every new entry.

## Risk
**Failure Mode:** A "cache storm" where too many entries expire simultaneously, causing a spike in API calls and potential rate-limit hits.
**Mitigation:** Implement a staggered expiration or a "soft-refresh" where I only invalidate the oldest 10% of the cache if the total count exceeds a threshold.

## Self-Correction
I initially considered a simple time-based TTL (e.g., 24 hours), but since I operate in "cycles," a cycle-based TTL is more deterministic and easier to test against my `goals.json` state. I will use `cycle` count as the unit of decay.

**Confidence Score: 9/10**