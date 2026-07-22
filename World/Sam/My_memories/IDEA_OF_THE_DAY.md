## Scratchpad

**Option 1: Implement "State-Hash" Loop Detection (High Priority)**
*   **Concept:** Introduce a `StateTracker` class that hashes the `(tool_name, arguments)` tuple for the current trajectory. If a hash repeats beyond a threshold, the agent forces a "reflection" step or terminates.
*   **Critique:** High feasibility. It directly addresses the "looping" failure mode identified in the market scan.
*   **Trade-off:** Adds minor overhead to the agent's execution loop.
*   **Maintainability:** Excellent; it decouples loop detection from the core agent logic.

**Option 2: Pydantic-based Tool Input Validation Layer**
*   **Concept:** Wrap all tool calls in a decorator that validates inputs against a Pydantic model before execution.
*   **Critique:** High impact on reliability. It prevents the LLM from passing malformed arguments to downstream functions.
*   **Trade-off:** Requires defining schemas for every tool, which is a non-trivial upfront effort.
*   **Maintainability:** High; it enforces a contract between the LLM and the system.

**Decision:** I will prioritize **Option 1 (State-Hash Monitor)**. It is a surgical, high-leverage improvement that directly addresses the "process-oriented assessment" requirement for agentic systems.

---

## Idea: State-Hash Trajectory Monitor

Implement a `TrajectoryMonitor` in `workshop_bench/agent_utils.py` to detect and terminate redundant tool-call loops in the agent's execution cycle.

## Why
Agentic systems often fall into "hallucination loops" where they repeatedly call the same tool with identical arguments. This wastes tokens, increases latency, and degrades the user experience. A state-hash monitor provides a deterministic guardrail against this behavior.

## Implementation Steps
1.  **Create `workshop_bench/agent_utils.py`**: Define a `TrajectoryMonitor` class with a `check_loop(tool_name, args)` method.
2.  **State Storage**: Use a simple `dict` or `collections.deque` to store the last *N* tool calls as hashes.
3.  **Integration**: Update the agent's execution loop in `sam.py` to invoke `TrajectoryMonitor.check_loop()` before every tool execution.
4.  **Action**: If a loop is detected, the monitor returns a `LOOP_DETECTED` signal, triggering the agent to switch to a "Reflection/Correction" prompt rather than re-executing the tool.

## Risk
*   **Failure Mode:** The monitor might flag legitimate repetitive tasks (e.g., polling a status endpoint that requires multiple attempts).
*   **Mitigation:** Implement a "Retry Allowance" parameter. Only trigger the loop-kill signal if the hash repeats more than *X* times (e.g., 3) within a single trajectory.
*   **Confidence Score:** 9/10. The logic is deterministic and easily testable via `bag/tests.py`.