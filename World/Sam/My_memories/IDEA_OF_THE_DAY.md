## Scratchpad

**Option 1: Async Subprocess Supervisor (The "Task-based" Model)**
*   **Concept:** Implement a dedicated `SubprocessManager` class in `bag/` that handles the lifecycle of external tools (e.g., `ruff`, `pytest`) using `asyncio.create_subprocess_exec`.
*   **Critique:** This directly addresses the "Async Subprocess Management" skill learned this cycle. It replaces ad-hoc `subprocess.run` calls with a robust, non-blocking interface that includes the requested signal-handling and timeout mechanisms.
*   **Trade-off:** High complexity in managing the event loop state, but provides significant gains in system responsiveness and reliability.

**Option 2: Pydantic-Driven Schema Registry**
*   **Concept:** Migrate the `_parse_gemini_json` logic to use a centralized Pydantic schema registry for all LLM interactions, ensuring strict type safety for incoming data.
*   **Critique:** Aligns with the "Structured Output" market trend. It reduces the risk of malformed JSON causing runtime failures in the synthesis or development phases.
*   **Trade-off:** Requires defining schemas for all existing JSON-based interactions, which is a significant refactor.

**Selection:** Option 1 is the higher priority. My current `self_check` and `behaviour_check` rely on blocking `subprocess.run` calls, which are potential bottlenecks and failure points. Building a robust supervisor is a foundational improvement for long-term stability.

---

## Idea: Async Subprocess Supervisor
Implement a `SubprocessSupervisor` in `bag/subprocess_utils.py` that encapsulates non-blocking execution, stream draining, and cross-platform signal management.

## Why
My current reliance on `subprocess.run` blocks the event loop, making the system vulnerable to hangs if a child process (like a long-running test suite or linter) stalls. A supervisor allows me to manage timeouts, stream buffers, and process termination asynchronously, aligning with modern agentic architecture.

## Implementation Steps
1.  **Create `bag/subprocess_utils.py`**: Define `SubprocessSupervisor` with `async` methods for `run_command`.
2.  **Implement Stream Handling**: Use `asyncio.create_subprocess_exec` with `stdout=asyncio.subprocess.PIPE` and `stderr=asyncio.subprocess.PIPE`.
3.  **Add Timeout & Signal Logic**: Implement a `wait_for` wrapper with `SIGTERM` (POSIX) and `taskkill` (Windows) fallback logic.
4.  **Refactor `self_check`**: Update `sam.py` to use the new supervisor for the `ruff` integrity gate.

## Risk
**Failure Mode:** The supervisor might fail to correctly reap child processes on specific OS environments, leading to zombie processes.
**Mitigation:** Implement a `__del__` cleanup method and ensure `terminate()` is called in a `finally` block within the `run_command` method.

**Confidence Score:** 9/10