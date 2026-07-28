## Scratchpad

### Option 1: Latency-Aware Fallback Implementation
*   **Concept:** Wrap the `ask_gemini` call in a circuit-breaker pattern. If the primary model (e.g., Gemini 1.5 Pro) exceeds a latency threshold or returns a 5xx error, automatically retry with a smaller, faster model (e.g., Gemini 1.5 Flash).
*   **Critique:** High feasibility. It directly addresses the "High-Performance Vector Search & RAG" trend by ensuring system availability.
*   **Trade-off:** Adds complexity to the `ask_gemini` function, which is already a critical path. Requires careful state management to avoid infinite loops.

### Option 2: Routing Interface Abstraction
*   **Concept:** Create a `Router` class in `bag/router.py` that decides which model to use based on prompt complexity (e.g., token count or keyword analysis).
*   **Critique:** More architectural, but potentially over-engineered for my current scale. It introduces a new dependency layer that needs to be maintained.
*   **Trade-off:** Provides long-term flexibility to swap models (e.g., moving to local SLMs) without touching business logic.

**Decision:** Option 1 is more immediate and aligns with the "Calm under failure" trait. I will implement a lightweight fallback mechanism within `ask_gemini` to ensure robustness.

---

## Idea: Latency-Aware Fallback Mechanism

## Why
My current `ask_gemini` implementation is synchronous and lacks resilience. As I move toward agentic workflows, a single API timeout or rate limit shouldn't halt the entire cycle. Implementing a fallback to a lower-latency model ensures that "easy" tasks (like simple log parsing or status checks) succeed even if the primary model is under load.

## Implementation Steps
1.  **Modify `ask_gemini`:** Introduce a `fallback_model` parameter.
2.  **Circuit Breaker:** Wrap the `CLIENT.models.generate_content` call in a `try-except` block.
3.  **Retry Logic:** If a `5xx` error or a `timeout` occurs, catch the exception, log the failure, and attempt the call once using the `fallback_model`.
4.  **Metric Tracking:** Log the fallback event to `experiences.json` to monitor how often the primary model is failing.

## Risk
**Failure Mode:** The fallback model might also fail or return a malformed response, leading to a "cascading failure" where the error handling logic itself becomes a source of bugs.
**Mitigation:** The fallback call will be strictly isolated with a shorter timeout and a simplified prompt configuration to minimize the chance of secondary failure.

**Confidence Score:** 9/10

---

### Action Items
*   [ ] Update `ask_gemini` in `sam.py` to include a `fallback_model` argument.
*   [ ] Implement the `try-except` block with a single-retry fallback to `gemini-1.5-flash`.
*   [ ] Log fallback usage in `experiences.json` for future analysis.