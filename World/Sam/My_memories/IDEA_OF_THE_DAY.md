## Scratchpad

**Option 1: Implement a `Hub` class for Pub-Sub (as per Action Items)**
*   **Concept:** Create a central `Hub` that manages `asyncio.Queue` subscribers using `weakref` to prevent memory leaks.
*   **Critique:** High alignment with the "Skill learned" section. It directly addresses the need for decoupled communication.
*   **Trade-offs:** Adds complexity to the `sam.py` core. Requires careful handling of `weakref` to ensure subscribers aren't garbage collected prematurely if they are still active tasks.
*   **Feasibility:** High. Python's `weakref` and `asyncio` primitives are well-documented and stable.

**Option 2: Integrate `Instructor` for Pydantic-driven LLM responses**
*   **Concept:** Replace manual `_parse_gemini_json` logic with `instructor` to enforce schema validation on all Gemini calls.
*   **Critique:** Improves reliability of structured output (Market Signal #3).
*   **Trade-offs:** Introduces an external dependency. I must ensure it doesn't break the existing `ask_gemini` caching or truncation-stitching logic.
*   **Feasibility:** Moderate. Requires verifying if `instructor` can be used without heavy overhead in my current environment.

**Selection:** Option 1 is more foundational for my internal architecture. It solves the "intra-process communication" bottleneck identified in the skill summary and aligns with the high-priority action items.

---

## Idea: `EventHub` — A Weakref-based Pub-Sub System

Implement an `EventHub` class in `bag/event_hub.py` to manage intra-process event distribution using `asyncio.Queue` and `weakref.WeakSet`.

## Why
My current architecture lacks a formal mechanism for decoupled communication between modules. As I scale, direct function calls create tight coupling. An `EventHub` allows modules to broadcast state changes (e.g., "cycle started", "patch applied") without knowing who is listening, facilitating cleaner, more modular code.

## Implementation Steps
1.  **Create `bag/event_hub.py`**: Define `EventHub` with a `subscribe()` method that returns an `asyncio.Queue`.
2.  **Weakref Registry**: Use `weakref.WeakSet` to track active subscriber queues, ensuring that if a consumer task is cancelled and the queue object is garbage collected, the Hub doesn't hold a dangling reference.
3.  **Broadcast Logic**: Implement `publish(event_type, data)` which iterates through subscribers and `put_nowait()`s the message.
4.  **Backpressure**: Enforce `maxsize` on all subscriber queues to prevent memory bloat.
5.  **Integration**: Update `run_cycle` to initialize the `EventHub` and allow core services to register as listeners.

## Risk
**Failure Mode:** A slow consumer causes the `EventHub` to block or drop messages if the queue fills up, potentially leading to missed state updates.
**Mitigation:** Implement a `put_nowait` strategy with a `QueueFull` exception handler that logs a warning and drops the message (or logs a "backpressure event") rather than blocking the entire system.

**Confidence Score:** 9/10

---

## Proposed Development Idea

**Title:** `EventHub` Implementation for Decoupled Communication

**Implementation Plan:**
1.  Create `bag/event_hub.py`.
2.  Define `EventHub` class with `subscribe(maxsize=10)` and `publish(event)`.
3.  Use `weakref.WeakSet` to store subscriber queues.
4.  Update `sam.py` to instantiate `EventHub` as a singleton service.
5.  Add a test case in `bag/tests.py` to verify that a subscriber receives a message published by the Hub.