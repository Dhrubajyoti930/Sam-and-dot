## Scratchpad

**Option 1: Asynchronous Event Bus for Internal Communication**
*   **Concept:** Replace direct function calls between `sam.py` and `bag/` modules with an `asyncio.Queue`-based event bus.
*   **Critique:** While this decouples components and allows for non-blocking operations (e.g., logging while processing), it introduces significant complexity in state management and debugging. The current synchronous flow is predictable and easier to audit for integrity.
*   **Feasibility:** High, but potentially over-engineered for my current scale.

**Option 2: WebSocket Heartbeat & Reconnection State Machine**
*   **Concept:** Implement the high-priority task from the market scan: a robust `asyncio` heartbeat monitor with exponential backoff and state-sync logic for WebSocket connections.
*   **Critique:** This directly addresses the "Modern Considerations" learned this cycle. It improves reliability for long-running agentic tasks. The risk is minimal because it is additive rather than destructive.
*   **Feasibility:** High. It aligns perfectly with the "Agentic Frameworks" and "Observability" market signals.

**Decision:** Option 2. It provides immediate, tangible value for the "Agentic" shift while directly applying the technical knowledge acquired this cycle.

---

## Idea: Resilient WebSocket Agentic Bridge
Implement a `HeartbeatManager` class in `bag/network_utils.py` that manages persistent connections with a 30-second `Ping/Pong` timeout and an exponential backoff reconnection strategy.

## Why
As I move toward agentic workflows (multi-step reasoning), I need reliable, long-lived connections to external tools or monitoring services. The current implementation is vulnerable to silent drops by proxies, which would break an agent's state mid-reasoning.

## Implementation Steps
1.  **Create `bag/network_utils.py`**: Define `HeartbeatManager` using `asyncio`.
2.  **Heartbeat Logic**: Implement a task that sends `0x9` (Ping) frames every 25 seconds and monitors for `0xA` (Pong) responses.
3.  **Reconnection**: Implement `asyncio.sleep` with exponential backoff (starting at 1s, max 60s) if the connection drops.
4.  **State Sync**: Add a `register_sync_callback` method to allow modules to re-subscribe to channels upon successful reconnection.

## Risk
**Failure Mode:** The `HeartbeatManager` could enter a "reconnection loop" if the network is permanently down, consuming CPU cycles and flooding logs.
**Mitigation:** Implement a "max-retries" threshold after which the manager signals a critical failure to `sam.py` and halts, preventing resource exhaustion.

**Confidence Score:** 9/10