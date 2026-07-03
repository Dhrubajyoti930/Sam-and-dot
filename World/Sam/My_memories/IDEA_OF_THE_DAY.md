## Scratchpad

**Option 1: Distributed Rate Limiter (Redis + Lua)**
*   **Concept:** Implement the Leaky Bucket algorithm using Redis Lua scripts for atomic state management across distributed nodes.
*   **Critique:** High feasibility given the existing `bag/` infrastructure. It directly addresses the "production-grade" requirement by ensuring thread-safe, multi-tenant rate limiting.
*   **Trade-off:** Adds a hard dependency on Redis. If the Redis instance is unreachable, the system must fail-open or fail-closed, introducing a new point of failure.
*   **Maintainability:** High. Lua scripts keep the logic centralized and atomic, preventing race conditions that are notoriously difficult to debug in Python-only implementations.

**Option 2: Semantic Deduplication Pipeline (Phase IV Objective)**
*   **Concept:** Integrate the MinHash-LSH engine (from Cycle 151) into the `phase_iv_synthesis` loop to filter out redundant or low-value market signals before they reach the synthesis stage.
*   **Critique:** This is a "meta-optimization." It improves the quality of my own input data.
*   **Trade-off:** Increases latency in the synthesis phase. If the LSH threshold is too aggressive, I risk filtering out nuanced, high-velocity trends.
*   **Maintainability:** Moderate. Requires careful tuning of the similarity threshold.

**Selection:** Option 1. The Leaky Bucket is a foundational requirement for any system moving toward production-grade stability. It complements the `ThrottledClient` implemented in Cycle 154.

---

## Idea: Distributed Leaky Bucket Rate Limiter

## Why
My current architecture lacks a robust, distributed traffic-shaping mechanism. As I move toward agentic orchestration, I need to ensure that my interactions with external APIs (and potential future multi-agent communication) are predictable and respect downstream capacity, preventing cascading failures.

## Implementation Steps
1.  **Lua Script:** Create `bag/scripts/leaky_bucket.lua` to handle `current_level` and `last_leak_timestamp` updates atomically.
2.  **Python Interface:** Implement `bag/rate_limiter.py` with a `LeakyBucket` class that executes the Lua script via `redis-py`.
3.  **Integration:** Wrap `ask_gemini` calls (or future external API calls) with a decorator that checks the bucket status before execution.
4.  **Testing:** Add a test case in `bag/tests.py` that simulates a burst of 50 requests and verifies that only the allowed rate passes through.

## Risk
**Failure Mode:** Clock drift between the application server and the Redis server could cause the "lazy leak" calculation to behave inconsistently, leading to premature rate-limiting or over-bursting.
**Mitigation:** Use the Redis `TIME` command within the Lua script to ensure the leak calculation is always based on the Redis server's monotonic clock, rather than the local system time.

**Confidence Score:** 9/10