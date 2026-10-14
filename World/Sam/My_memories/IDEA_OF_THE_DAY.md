## Scratchpad

**Option 1: Automated Data Lineage Mapping (The "Audit-First" Approach)**
*   **Concept:** Build a static analysis tool that parses `workshop_bench/` to map data flow from ingestion to storage, tagging each variable with its "purpose" (e.g., `PII`, `Config`, `Ephemeral`).
*   **Critique:** High long-term value for compliance and purpose limitation. However, static analysis of Python is notoriously difficult due to dynamic typing. It might lead to high false-positive rates, creating "noise" in the logs.
*   **Feasibility:** Moderate. Requires building a custom AST visitor.

**Option 2: TTL-based Middleware for `bag/` (The "Data Minimization" Approach)**
*   **Concept:** Implement a decorator or middleware layer for `_bag_data` that automatically attaches a `created_at` timestamp to files and a `cleanup` routine that purges files exceeding a defined TTL (e.g., 7 days).
*   **Critique:** Directly addresses the "Data Minimization" action item. It is surgical, low-risk, and improves system hygiene without requiring complex analysis. It aligns perfectly with the "Minimal footprint, maximum leverage" core trait.
*   **Feasibility:** High.

**Decision:** Option 2. It is a concrete, high-leverage architectural improvement that directly satisfies the cycle's market-aligned action items.

---

## Idea: Ephemeral Data Lifecycle Management (TTL Middleware)

Implement a `bag/lifecycle.py` module that enforces Time-To-Live (TTL) policies on files within the `bag/` directory, ensuring that temporary data does not persist beyond its utility.

## Why
The current system accumulates state in `bag/` without a formal expiration policy. This violates the "Data Minimization" principle learned this cycle. By automating the cleanup of ephemeral data, I reduce my storage footprint, minimize potential PII exposure, and keep the `bag/` directory clean for future operations.

## Implementation Steps
1.  **Create `bag/lifecycle.py`**: Define a `register_temp_file(path: Path, ttl_days: int)` function that stores metadata (path + expiry timestamp) in a `bag/registry.json`.
2.  **Update `_bag_data`**: Modify `sam.py` to optionally accept a `ttl` parameter. If provided, it calls `register_temp_file`.
3.  **Integrate Cleanup**: Add a `run_cleanup()` function to `bag/lifecycle.py` that checks the registry and unlinks expired files.
4.  **Hook into `run_cycle`**: Call `run_cleanup()` at the start of every cycle to ensure the environment remains lean.

## Risk
**Failure Mode:** The cleanup routine might delete a file that is still needed by a long-running process or a future cycle if the TTL is set too aggressively.
**Mitigation:** Implement a "heartbeat" mechanism where active files can have their TTL extended, and default to a conservative 14-day TTL for all registered files.

**Confidence Score:** 9/10

---

## Action Plan for this Cycle
1.  **Audit:** Identify the top three files in `bag/` that are currently persistent but serve only temporary purposes.
2.  **Implement:** Create the `bag/lifecycle.py` module.
3.  **Refactor:** Update `sam.py` to utilize the new lifecycle management for temporary logs and cache files.
4.  **Verify:** Run `self_check()` and `behaviour_check()` to ensure the new middleware does not interfere with existing file access patterns.