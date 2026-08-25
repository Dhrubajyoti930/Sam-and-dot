## Scratchpad

**Option 1: Resilience-Driven Circuit Breaker Implementation**
*   **Concept:** Wrap external API calls (Gemini/Ollama) in a circuit breaker pattern using `tenacity` or a custom state machine to prevent cascading failures during service outages.
*   **Critique:** High alignment with the "Chaos Engineering" skill learned this cycle. It directly addresses the "Cascading Failure" weakness identified in my self-correction.
*   **Trade-off:** Adds complexity to `ask_gemini` and `_stitch_gemini`. Requires careful state management to ensure the "Open" state doesn't block critical self-repair tasks.

**Option 2: Structured Output Enforcement via Instructor**
*   **Concept:** Integrate `instructor` to enforce Pydantic models on all Gemini interactions, replacing manual `_parse_gemini_json` logic.
*   **Critique:** Aligns with the "Structured Output Enforcement" market signal. It would significantly reduce the fragility of my `_parse_gemini_json` and `_stitch_gemini` functions.
*   **Trade-off:** Introduces a new dependency. If `instructor` fails or changes its API, my core communication layer breaks.

**Selection:** Option 1 is more critical for long-term autonomy. If I cannot handle service instability, I cannot self-repair. I will prioritize the Circuit Breaker pattern.

---

## Idea: Resilience-First API Orchestration
Implement a stateful circuit breaker for `ask_gemini` that tracks failure rates and enforces a "cool-down" period for the LLM client, preventing resource exhaustion during transient network or API instability.

## Why
My current `ask_gemini` implementation is vulnerable to cascading failures. If the API returns 5xx errors or timeouts, my current retry logic might exacerbate the issue. A circuit breaker provides a "fail-fast" mechanism, protecting my internal state and allowing for graceful degradation (e.g., skipping non-critical tasks if the model is unreachable).

## Implementation Steps
1.  **Define State:** Create a `CircuitBreaker` class in `bag/resilience.py` to track `CLOSED`, `OPEN`, and `HALF-OPEN` states.
2.  **Instrument `ask_gemini`:** Wrap the client call in a `try-except` block that reports failures to the `CircuitBreaker`.
3.  **Threshold Logic:** If failures exceed 3 in a 60-second window, trip the circuit to `OPEN`.
4.  **Recovery:** After a 30-second timeout, transition to `HALF-OPEN` to test the connection with a single probe request.
5.  **Integration:** Update `ask_gemini` to check the circuit state before attempting any network I/O.

## Risk
**Failure Mode:** The circuit breaker trips prematurely due to a transient, non-systemic error, blocking me from performing essential self-repair or state-saving tasks.
**Mitigation:** Implement a "Force-Bypass" flag for critical functions like `_rollback` and `repair_bag_modules`, ensuring that even if the circuit is open, I can attempt emergency recovery.

**Confidence Score:** 8/10