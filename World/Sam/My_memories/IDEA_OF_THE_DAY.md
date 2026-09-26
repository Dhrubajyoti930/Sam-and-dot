## Scratchpad

**Option 1: Implement an "Eval-Driven" Regression Suite (Phase V/VI)**
*   **Concept:** Integrate `Ragas` or a custom lightweight evaluation harness into `bag/tests.py` to benchmark my own code-generation patches against a set of "golden" prompt-response pairs.
*   **Critique:** High long-term value for stability. However, it requires building a dataset of "correct" patches, which is a significant upfront investment. It might be overkill for my current scale.
*   **Feasibility:** Moderate.

**Option 2: Transition to SSE for Internal Agent Communication (Phase V)**
*   **Concept:** Replace the current polling-based status checks in `run_cycle` with an SSE-based event stream for real-time monitoring of long-running tasks (like `ask_gemini` continuations).
*   **Critique:** Aligns with the "Real-Time Communication" skill learned this cycle. It reduces latency and resource overhead. It is a cleaner architectural pattern than polling.
*   **Feasibility:** High. It leverages existing `sam.py` infrastructure.

**Decision:** Option 2. It directly applies the cycle's learned skill to improve my internal operational efficiency.

---

## Idea
**SSE-Based Event Stream for Operational Monitoring**

## Why
Currently, my cycle monitoring relies on polling `cycle_status` files. This is inefficient and introduces artificial latency. Implementing an SSE-based stream allows me to push real-time updates (e.g., "Gemini call started," "Patch applied," "Integrity Gate passed") to a local monitoring endpoint, improving observability without increasing resource consumption.

## Implementation Steps
1.  **Define Event Schema:** Create a simple `Event` Pydantic model in `bag/schemas.py` to standardize log messages (timestamp, level, message, component).
2.  **Refactor `log` utility:** Update the internal `log` function to broadcast events to a local `asyncio.Queue` that acts as an event bus.
3.  **Implement SSE Server:** Add a lightweight `FastAPI` or `starlette` route in a new `bag/monitor.py` that yields events from the queue to connected clients.
4.  **Update `run_cycle`:** Integrate the event emitter into the core loop to push status updates as they happen.

## Risk
**Failure Mode:** The SSE connection might hang or block the main execution thread if not handled with proper `asyncio` non-blocking patterns.
**Mitigation:** Use `asyncio.Queue` with `put_nowait()` to ensure logging never blocks the primary logic. Wrap the SSE server in a separate thread or process to isolate it from the main `run_cycle` execution.

**Confidence Score:** 9/10