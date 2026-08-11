## Scratchpad

### Option 1: Actor-Model Task Queue
*   **Concept:** Refactor the current `task-queue` module to use an actor-like mailbox pattern.
*   **Critique:** 
    *   *Pros:* Eliminates shared-state race conditions; aligns with the "Actor Model" skill learned this cycle.
    *   *Cons:* High complexity for a single-threaded Python script. The overhead of managing mailboxes might be overkill unless I introduce true concurrency (e.g., `asyncio` or `multiprocessing`).
    *   *Feasibility:* Moderate. Requires significant changes to how `task-queue` interacts with the global state.

### Option 2: Supervisor-Style Error Boundary
*   **Concept:** Implement a supervisor-style error boundary for the network-request module (specifically `ask_gemini` and related calls).
*   **Critique:**
    *   *Pros:* Directly addresses the "let it crash" philosophy. Improves resilience against transient API failures or network timeouts.
    *   *Cons:* Requires careful implementation of the "at-least-once" delivery logic to ensure state consistency.
    *   *Feasibility:* High. I already have `_rollback` and `_alert_dot` logic; this is a natural extension of my existing recovery infrastructure.

**Decision:** Option 2 is more aligned with my current need for stability and aligns with the "Actor Model" supervision hierarchy concept without requiring a full rewrite of my execution engine.

---

## Idea: Supervisor-Pattern for Network Resilience

Implement a `Supervisor` class in `bag/network_resilience.py` that wraps `ask_gemini` calls. This supervisor will manage retries, exponential backoff, and state-checkpointing, treating each network request as a supervised child process.

## Why
My current network calls are vulnerable to transient failures. By formalizing the supervision hierarchy, I can ensure that if a request fails, the supervisor handles the retry logic or triggers a graceful degradation/rollback, rather than letting the failure bubble up to the main cycle loop.

## Implementation Steps
1.  **Create `bag/network_resilience.py`**: Define a `Supervisor` class that accepts a task (the network call) and a retry policy.
2.  **Encapsulate `ask_gemini`**: Move the retry logic currently inside `ask_gemini` into the `Supervisor`.
3.  **Implement Checkpointing**: Before executing a request, the supervisor will log the intent to a temporary file. If the process crashes, the next cycle can detect the pending request and decide whether to resume or discard.
4.  **Integrate**: Update `sam.py` to route all `ask_gemini` calls through the `Supervisor`.

## Risk
*   **Failure Mode:** The supervisor itself could enter an infinite retry loop if the error is non-transient (e.g., invalid API key or model deprecation).
*   **Mitigation:** Implement a "Circuit Breaker" pattern within the supervisor that trips after $N$ failed attempts, forcing a hard stop and an alert to Dot.
*   **Confidence Score:** 8/10. The logic is well-defined, but the integration into `sam.py` requires careful handling of existing global state.