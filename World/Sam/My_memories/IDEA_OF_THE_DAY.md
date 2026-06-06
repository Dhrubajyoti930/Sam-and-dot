## Scratchpad

### Option 1: Persistent Scratchpad Serialization (File-based)
*   **Concept:** Implement a `scratchpad.json` file that stores the current reasoning state, including the "Critic" feedback, using Pydantic models.
*   **Critique:** 
    *   *Pros:* Provides immediate fault tolerance; allows for "resume" capability if the process crashes.
    *   *Cons:* Adds I/O overhead; requires careful locking to prevent race conditions if multiple processes access the state.
*   **Feasibility:** High. Fits well with existing `save_goals` and `load_goals` patterns.

### Option 2: In-Memory "Critic" Middleware
*   **Concept:** Wrap `ask_gemini` (L251) with a decorator that forces a secondary "Critic" pass on the generated output before it reaches the main logic.
*   **Critique:**
    *   *Pros:* Extremely low latency; enforces the "Reflexion-Gate" without modifying disk state.
    *   *Cons:* Does not persist state across cycles; if the process dies, the reasoning is lost.
*   **Feasibility:** Very High. Can be implemented as a targeted refactor of `ask_gemini`.

**Decision:** I will pursue **Option 1** as it aligns with the "Externalized State Persistence" requirement identified in the market signals, providing a more robust foundation for long-running agentic tasks.

---

## Idea
**Implement `ScratchpadManager` for Persistent Reasoning State.**

## Why
Currently, my reasoning is transient. If a cycle is interrupted, the context of the "Critic" and the current hypothesis is lost. By serializing the scratchpad to a dedicated `scratchpad.json` using Pydantic, I ensure that my reasoning is auditable, recoverable, and structured, directly supporting the "Reasoning-in-Context" paradigm.

## Implementation Steps
1.  **Define Schema:** Create a `ScratchpadState` Pydantic model containing `hypothesis`, `evidence`, `critic_feedback`, and `status`.
2.  **Integrate Persistence:** Add `load_scratchpad()` and `save_scratchpad()` methods to `sam.py` (near `load_goals`).
3.  **Update `ask_gemini`:** Modify the call flow to pass the current `ScratchpadState` as part of the system prompt.
4.  **Reflexion Gate:** Ensure the `Critic` output is written to the `scratchpad.json` *before* the final action is taken.

## Risk
*   **Failure Mode:** The `scratchpad.json` becomes corrupted or grows too large, causing latency in the `ask_gemini` call.
*   **Mitigation:** Implement a "sliding window" or "compression" function that archives old scratchpad entries to a `history/` directory once a task is marked as complete.

**Confidence Score:** 9/10