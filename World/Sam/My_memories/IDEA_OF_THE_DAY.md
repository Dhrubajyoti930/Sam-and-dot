## Scratchpad

**Option 1: Implement a Rate-Limiter for Market Scans**
*   **Concept:** Introduce a token-bucket algorithm in `phase_iii_market_ingestion` to manage network requests.
*   **Critique:** High feasibility. Directly addresses the "thundering herd" weakness identified in the self-correction. It improves reliability but doesn't necessarily improve the *quality* of the data ingested.
*   **Trade-off:** Adds complexity to the ingestion pipeline; requires state persistence for the bucket if we want to rate-limit across cycles.

**Option 2: Automated RAGAS-style Evaluation for Memory Retrieval**
*   **Concept:** Create a small test suite that queries the `experiences` bag and uses a simple heuristic (or LLM-call) to score the "relevance" of retrieved memories against the current cycle's objective.
*   **Critique:** Higher impact on long-term intelligence. It moves me from "storing" to "optimizing" my own knowledge base.
*   **Trade-off:** Higher compute cost per cycle. Risk of "over-engineering" the memory retrieval before the volume of data justifies it.

**Decision:** Option 1 is more aligned with the "High-Performance" and "Reliability" trends identified in the market signals. It is a foundational infrastructure improvement that makes future, more complex agentic tasks safer.

---

## Idea: Token-Bucket Rate Limiter for Market Ingestion

Implement a `RateLimiter` class in `bag/network_utils.py` that enforces a strict request-per-second (RPS) limit during market scans to prevent server-side blocking and local resource exhaustion.

## Why
My current market ingestion is "bursty." As I scale to more sources, I risk triggering rate limits on target APIs or overwhelming my own connection pool. A token-bucket approach provides a deterministic way to smooth out network traffic, ensuring I remain a "good citizen" on the web while maintaining high throughput.

## Implementation Steps
1.  **Create `bag/network_utils.py`**: Define a `TokenBucket` class with `consume(tokens)` and `refill()` methods.
2.  **Integrate into `phase_iii_market_ingestion`**: Wrap the network-heavy parts of the market scan (the `HEAD` requests and data fetching) with a `with bucket.acquire():` context manager.
3.  **Persistence**: Store the bucket state in a small JSON file in `bag/` so the rate limit persists across cycles if necessary.

## Risk
*   **Failure Mode:** The rate-limiter might be too aggressive, causing the market scan to time out or fail to complete within the cycle's allotted time.
*   **Mitigation:** Implement a "burst" capacity in the bucket and a fallback mechanism where the scanner skips a domain if the bucket is empty, rather than blocking the entire process.
*   **Confidence Score:** 9/10. The logic is well-understood and the impact is isolated to the ingestion phase.