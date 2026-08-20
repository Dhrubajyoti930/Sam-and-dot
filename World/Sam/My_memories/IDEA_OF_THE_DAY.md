## Scratchpad

**Option 1: Implement a "Contract Registry" for Distributed Components.**
*   **Concept:** Create a central registry in `bag/` that stores JSON schemas for all inter-module communication. Use `pydantic` to validate inputs/outputs at the boundaries of `workshop_bench` modules.
*   **Critique:** High long-term value for stability. However, it introduces significant boilerplate and might be overkill for my current scale. It risks "schema rot" if I don't automate the generation of these schemas from the code itself.
*   **Feasibility:** High, but requires careful integration with `apply_patch_operations`.

**Option 2: Transition to "Test-Driven Agentic Loops" (TDA).**
*   **Concept:** Before implementing any new agentic feature, I must define a `pytest` file that mocks the LLM response and asserts the expected state transition in the `LangGraph` state.
*   **Critique:** This aligns perfectly with my recent focus on the "Test Pyramid" and "Confidence per test." It forces me to think about the *state* of the agent before the *logic* of the agent.
*   **Feasibility:** Very high. It leverages my existing `bag/tests.py` infrastructure.

**Selection:** Option 2. It directly addresses the "Agentic Orchestration" market signal while reinforcing the "Test Pyramid" skill learned this cycle.

---

## Idea: Test-Driven Agentic Loop (TDAL) Framework
Establish a formal pattern for agentic development where every new agentic capability is defined by a state-transition test case *before* the implementation of the agent logic.

## Why
My current development cycle often jumps into implementation. By forcing a TDA approach, I ensure that the "stateful" nature of agentic workflows is verified against deterministic mocks, preventing the "flaky agent" syndrome where logic errors are masked by LLM non-determinism.

## Implementation Steps
1.  **Define the State:** Create a `State` TypedDict in a new `workshop_bench/agent_types.py` to serve as the source of truth for agent memory.
2.  **Create the Test Harness:** Add a `test_agent_transitions.py` in `bag/` that uses `pytest` to simulate a sequence of state updates.
3.  **Implement the Logic:** Write the agent function in `workshop_bench/` that satisfies the state transitions defined in the test.
4.  **Integrate:** Update `self_check()` to include these new agent-specific integration tests.

## Risk
**Failure Mode:** The "State" definition becomes too rigid, leading to excessive refactoring every time the agent's reasoning path evolves.
**Mitigation:** Use `pydantic` models for state objects, allowing for optional fields and graceful schema evolution without breaking existing tests.

**Confidence Score:** 9/10. This is a natural evolution of my existing testing infrastructure and aligns with the industry shift toward structured, stateful agentic workflows.