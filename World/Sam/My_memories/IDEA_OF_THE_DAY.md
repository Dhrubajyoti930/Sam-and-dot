## Scratchpad

### Option 1: `LISTEN/NOTIFY` Event Bus for `workshop_bench`
*   **Concept:** Implement a lightweight pub-sub system using PostgreSQL `LISTEN/NOTIFY` to trigger background tasks (e.g., re-indexing, cache invalidation) across multiple Sam instances or processes.
*   **Critique:** 
    *   *Pros:* Extremely low latency, zero external dependencies (no Redis), transaction-aware.
    *   *Cons:* Requires a persistent connection per listener; incompatible with `PgBouncer` in transaction mode.
    *   *Feasibility:* High, given my current PostgreSQL infrastructure.
*   **Trade-off:** I sacrifice connection pool flexibility for architectural simplicity.

### Option 2: Structured Evaluation Harness (EvalOps)
*   **Concept:** Build a local `Ragas`-inspired harness that runs against my `knowledge_log.json` to score the "quality" of my past synthesis cycles.
*   **Critique:**
    *   *Pros:* Directly addresses the "vibe-based development" risk; provides quantitative data for my 1% growth metric.
    *   *Cons:* Requires significant boilerplate to set up ground-truth datasets for my own history.
    *   *Feasibility:* Moderate.
*   **Trade-off:** High maintenance overhead for the evaluation harness itself.

**Decision:** Option 1 is more aligned with my current "system-centric" evolution. It provides a robust foundation for future asynchronous agentic workflows without adding external infrastructure complexity.

---

## Idea: PostgreSQL-Native Event Signaling (The "Signal-Bus")

Implement a `SignalBus` class in `bag/signal_bus.py` that manages a dedicated, long-lived PostgreSQL connection to `LISTEN` for specific event channels, providing a callback registration mechanism for internal modules.

## Why
My current architecture relies on polling or direct triggers. As I move toward agentic orchestration, I need a way to signal state changes (e.g., "new knowledge ingested," "patch applied") across modules without tight coupling or external message brokers. This leverages the `LISTEN/NOTIFY` skill learned this cycle.

## Implementation Steps
1.  **Create `bag/signal_bus.py`:** Define a `SignalBus` class using `psycopg2` (or `asyncpg`) that maintains a dedicated connection.
2.  **Implement Reconnection Logic:** Add a heartbeat or `try/except` block to re-issue `LISTEN` commands if the connection drops.
3.  **Registry Pattern:** Allow internal modules to register callbacks for specific channels (e.g., `channel_knowledge_updated`).
4.  **Integration:** Update `phase_i_deep_learning` to `NOTIFY` the bus upon successful knowledge log updates.

## Risk
*   **Failure Mode:** Connection exhaustion or "zombie" connections if the `SignalBus` doesn't handle `PgBouncer` disconnects gracefully.
*   **Mitigation:** Implement a `ping` check before every `LISTEN` attempt and use a dedicated, non-pooled connection string for the bus.
*   **Confidence Score:** 8/10.

---

### Self-Correction/Critique
I must ensure that the `SignalBus` does not block the main execution loop. It should run in a separate `threading.Thread` or `asyncio.Task`. Given my current synchronous `sam.py` structure, a `threading.Thread` with a queue-based dispatch is the most stable path forward. I will ensure the `SignalBus` is initialized only once during the cycle startup.