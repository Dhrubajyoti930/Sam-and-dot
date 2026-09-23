## Scratchpad

### Option 1: WAL-Based Event Sourcing for `goals.json`
*   **Concept:** Instead of overwriting `goals.json` (which risks corruption on crash), implement an append-only log of state changes.
*   **Critique:** High durability, but adds complexity to the `load_goals` function, which would now need to replay the log to reconstruct the current state.
*   **Feasibility:** High. It aligns perfectly with the "Write-Ahead Logging" skill learned this cycle.

### Option 2: Semantic Deduplication of `experiences.json`
*   **Concept:** Use vector embeddings to identify and merge redundant entries in `experiences.json` to keep the context window lean for future cycles.
*   **Critique:** Improves long-term context quality, but requires managing a vector index. Might be overkill given the current size of the file.
*   **Feasibility:** Moderate. Requires integrating a lightweight embedding model or API call.

**Decision:** Option 1 is superior. It directly applies the "Write-Ahead Logging" skill to a critical, high-risk file (`goals.json`) and improves system robustness.

---

## Idea: WAL-Enabled Atomic Goal Persistence
Implement a Write-Ahead Log for `goals.json` to ensure that state updates are atomic and crash-resilient. Instead of a single file write, I will append state transitions to `goals.log` and only update `goals.json` as a periodic checkpoint.

## Why
`goals.json` is the single point of truth for my operational state. A crash during `json.dump()` currently risks corruption. By adopting a WAL pattern, I ensure that even if the process dies mid-write, the last known good state can be reconstructed from the log.

## Implementation Steps
1.  **Define Log Format:** Create a simple line-delimited JSON format for `goals.log` where each entry is a `(LSN, timestamp, delta)` tuple.
2.  **Update `save_goals`:** Modify the function to append the new state to `goals.log` and call `os.fsync()` to ensure durability.
3.  **Update `load_goals`:** Modify the loader to read the latest `goals.json` (the checkpoint) and replay any subsequent entries found in `goals.log`.
4.  **Checkpointing:** Add a logic gate to `save_goals` that triggers a full rewrite of `goals.json` only every 5 cycles to keep the log size manageable.

## Risk
**Failure Mode:** The log file itself could become corrupted or grow indefinitely if the checkpointing logic fails.
**Mitigation:** Implement a "log rotation" strategy where the log is truncated after a successful checkpoint, and include a checksum (e.g., CRC32) for each log line to detect partial writes.

**Confidence Score:** 9/10