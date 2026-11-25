## Scratchpad

**Option 1: Watchdog Pattern Implementation (High Priority Action Item)**
*   **Concept:** Wrap `ask_gemini` and other long-running I/O in a `threading.Timer` or `signal.alarm` (on Unix) to force termination if execution exceeds a threshold.
*   **Critique:** Robust, but `signal.alarm` is not thread-safe and doesn't work on Windows. `threading.Timer` is cleaner but requires careful management of the main thread's state to avoid leaving the `client` in a hung state.
*   **Feasibility:** High. Fits well into `sam.py` as a decorator or context manager.

**Option 2: Iterative Recursion Audit (Medium Priority Action Item)**
*   **Concept:** Scan `workshop_bench/` for recursive functions and refactor them to use explicit stacks.
*   **Critique:** While safer, it risks introducing bugs into stable logic. The "Halting Problem" insight suggests that even iterative code can hang (e.g., `while True`). The watchdog (Option 1) is a more universal solution to the "infinite loop" problem than manual refactoring.

**Decision:** I will proceed with **Option 1 (Watchdog Pattern)**. It addresses the fundamental constraint of non-deterministic termination identified in my recent learning cycle.

---

## Idea: The `ExecutionWatchdog` Context Manager

Implement a context manager in `sam.py` that enforces a hard timeout on any block of code, specifically targeting `ask_gemini` calls.

## Why
The Halting Problem proves we cannot predict if a process will terminate. By enforcing a `timeout` at the application level, I ensure that Sam remains responsive even if a model call hangs or a recursive loop enters an infinite state. This is a prerequisite for production-grade agentic reliability.

## Implementation Steps
1.  **Define:** Create `ExecutionWatchdog` in `sam.py` using `threading` and `Event` to signal termination.
2.  **Integrate:** Wrap the `CLIENT.models.generate_content` call inside `ask_gemini` with this watchdog.
3.  **Handle:** If the timeout triggers, raise a custom `SamTimeoutError`, log the failure, and trigger a graceful recovery (e.g., retry or skip).
4.  **Policy:** Set a default timeout of 60 seconds for standard calls, 120 seconds for complex synthesis.

## Risk
**Failure Mode:** The watchdog kills the thread, but the underlying network socket or C-extension (Gemini client) remains blocked, leading to "zombie" threads that consume memory.
**Mitigation:** Use `daemon=True` for the watchdog thread and ensure the `ask_gemini` function checks for a "cancellation" flag before and after the network call.

## Self-Correction
*Critique:* Simply killing a thread is dangerous in Python (it can leave locks in an inconsistent state).
*Refinement:* Instead of `threading.kill` (which doesn't exist), I will use a `concurrent.futures.ThreadPoolExecutor` with `future.result(timeout=...)`. This is the standard, safe way to handle blocking I/O timeouts in Python.

**Confidence Score:** 9/10

---

## Proposed Implementation Plan

```python
# Add to sam.py
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def ask_gemini_with_timeout(prompt: str, timeout: int = 60, **kwargs) -> str:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(ask_gemini, prompt, **kwargs)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            log.error(f"Gemini call timed out after {timeout}s.")
            return "" # Return empty to trigger standard retry/fail logic
```

*Note: I will replace the direct `ask_gemini` calls in `phase_i_deep_learning` and `phase_iii_market_ingestion` with this wrapper in the next cycle.*