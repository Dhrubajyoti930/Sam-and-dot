## Scratchpad

### Option 1: Redis Cluster Client-Side Routing
*   **Concept:** Implement a `ClusterClient` wrapper that maintains a local cache of the 16,384 hash slots and handles `MOVED` redirections automatically.
*   **Critique:** High complexity. Requires maintaining a persistent connection pool to all master nodes and handling cluster topology changes (e.g., re-sharding). While it aligns with the "Redis Clustering" skill learned, it might be overkill for my current scale.
*   **Feasibility:** Moderate.

### Option 2: Atomic Lua-based Multi-Key Operations
*   **Concept:** Since I am already using Redis Lua scripts for rate-limiting, I can extend this to perform atomic multi-key operations (e.g., `MGET` across shards) by using `EVAL` to execute logic server-side, bypassing the "No Cross-Slot Transactions" constraint by grouping related keys via Hash Tags.
*   **Critique:** This leverages my existing Redis infrastructure and directly addresses the "No Cross-Slot Transactions" weakness identified in my self-correction. It is more maintainable than a full cluster client.
*   **Feasibility:** High.

**Decision:** Option 2. It builds on my existing Redis/Lua architecture and directly mitigates the cross-slot transaction limitation.

---

## Idea: Atomic Hash-Tag Orchestrator for Redis
Implement a `RedisOrchestrator` utility that enforces the use of Hash Tags (`{tag}`) for all multi-key operations, ensuring that related data (e.g., `user_id` context) is always co-located on the same shard, and providing a Lua-based wrapper for atomic multi-key updates.

## Why
My current Redis implementation is vulnerable to cross-slot errors when performing multi-key operations. By formalizing a "Hash Tag" policy and providing a wrapper that validates key-grouping before execution, I ensure data integrity and prevent runtime `CROSSSLOT` errors in my event-sourcing pipeline.

## Implementation Steps
1.  **Define `HashTagManager`:** Create a utility in `bag/redis_utils.py` that generates keys with mandatory `{tag}` prefixes.
2.  **Lua Wrapper:** Implement a `multi_update.lua` script that accepts a list of keys and values, validates that all keys share the same hash tag, and executes the update atomically.
3.  **Validation Gate:** Add a decorator `@enforce_hash_tag` to my Redis-interacting methods that checks if the provided keys share the same `{tag}` before sending the command to Redis.
4.  **Test:** Add a test case in `bag/tests.py` that attempts a cross-slot operation and verifies that the `HashTagManager` raises a `ValueError` before the command reaches the server.

## Risk
**Failure Mode:** If the logic for extracting the hash tag from a key is flawed, I could inadvertently force unrelated keys into the same shard, creating a "hot shard" bottleneck.
**Mitigation:** Implement a strict regex-based validator for hash tags and include a "shard-balance" check in the `RedisOrchestrator` to monitor key distribution across slots.

**Confidence Score:** 9/10