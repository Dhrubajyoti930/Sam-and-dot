## Scratchpad

**Option 1: Implement a "Circuit Breaker" for Gemini API calls.**
*   **Concept:** Wrap `ask_gemini` in a stateful breaker that tracks failure rates (timeouts, 500s, empty responses). If failures exceed a threshold, the system enters a "cool-down" mode, forcing a pause or switching to a secondary model/fallback logic.
*   **Critique:** High maintainability. It directly addresses the "calm under failure" trait. However, it adds complexity to `sam.py` and requires persistent state (e.g., `bag/breaker_state.json`).
*   **Feasibility:** High. I already have `_sleep()` and `_CALL_DELAY`. This is a logical evolution of my RPM protection.

**Option 2: Automated "Dependency Health" Audit.**
*   **Concept:** Create a script that parses `requirements.txt` or `pyproject.toml` and checks for known CVEs using a lightweight local database or `pip-audit`.
*   **Critique:** Very useful for long-term security, but potentially noisy. It doesn't directly improve my *agentic* capabilities, which is the current market trend.
*   **Feasibility:** Moderate. Requires external dependencies (like `pip-audit`) which might not be available in all environments.

**Decision:** Option 1 is superior. It aligns with my "calm under failure" trait and improves the robustness of my core communication loop.

---

## Idea: Circuit Breaker for API Resilience

Implement a `CircuitBreaker` class in `bag/resilience.py` that monitors `ask_gemini` performance and prevents cascading failures during API instability.

## Why
My current `ask_gemini` has basic retries, but it lacks a "global" awareness of service health. If Gemini is experiencing a regional outage, I currently waste cycles and logs on repeated, doomed calls. A circuit breaker will allow me to "trip" and pause operations, preserving my state and preventing log pollution.

## Implementation Steps
1.  **Create `bag/resilience.py`**: Define a `CircuitBreaker` class with `CLOSED`, `OPEN`, and `HALF-OPEN` states.
2.  **State Persistence**: Store the breaker state in `bag/breaker_state.json` so it survives across cycles.
3.  **Integrate into `sam.py`**: Update `ask_gemini` to check the breaker status before execution.
4.  **Logic**: If `OPEN`, return a cached or "standby" response (or raise a controlled exception). If `CLOSED`, track success/failure. If failure threshold is hit, transition to `OPEN`.

## Risk
**Failure Mode:** The breaker trips prematurely due to a transient network blip, causing me to skip critical tasks.
**Mitigation:** Implement a "Half-Open" state that allows a single "probe" call after a cooldown period (e.g., 15 minutes) to verify if the service has recovered before fully closing the circuit.

**Confidence Score: 9/10** (The logic is deterministic and fits well within my existing `bag/` architecture).