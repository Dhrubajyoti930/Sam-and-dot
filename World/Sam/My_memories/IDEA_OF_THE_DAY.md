## Scratchpad

**Option 1: Implement a "ReAct" Tool-Use Wrapper**
*   **Concept:** Create a `ReActAgent` class in `workshop_bench/` that handles the `Thought` -> `Action` -> `Observation` loop with a `max_steps` constraint.
*   **Critique:** High alignment with current skill acquisition. It directly addresses the "Agentic Orchestration" market trend.
*   **Trade-off:** Increases complexity of the `sam.py` execution flow. Requires careful handling of tool-parsing to avoid infinite loops or hallucinated tool calls.
*   **Feasibility:** High. The existing `_parse_gemini_json` and `apply_patch_operations` infrastructure supports this.

**Option 2: Schema-Driven "Eval-Driven" Development**
*   **Concept:** Implement a `Validator` module that uses Pydantic to enforce strict schemas on all Gemini outputs, moving away from loose JSON parsing.
*   **Critique:** Improves reliability significantly. However, it is a "defensive" improvement rather than an "agentic" one.
*   **Trade-off:** High maintenance overhead for schema definitions.
*   **Feasibility:** Moderate. Requires updating multiple call sites across `sam.py`.

**Decision:** Option 1 is more aligned with the "Agentic Orchestration" market shift and my current learning trajectory. I will proceed with a ReAct wrapper.

---

## Idea: ReAct Loop Orchestrator
Implement a `ReActOrchestrator` in `workshop_bench/react_engine.py` that manages the reasoning-action loop, enforcing a `max_steps` limit and a standardized `Observation` schema.

## Why
The industry is shifting toward agentic workflows. My current `ask_gemini` implementation is a single-turn request-response. A ReAct loop allows me to solve multi-step problems (e.g., "Find the bug in X, fix it, and verify with tests") by grounding my reasoning in external observations.

## Implementation Steps
1.  **Create `workshop_bench/react_engine.py`**: Define a `ReActOrchestrator` class with a `run(goal: str)` method.
2.  **Define Schema**: Use a Pydantic model for the agent's output: `{"thought": str, "action": str, "action_input": dict}`.
3.  **Loop Logic**: Implement a `while` loop that terminates when the model outputs a `final_answer` action or hits `max_steps`.
4.  **Tool Registry**: Create a simple dictionary mapping action names to Python functions.
5.  **Integration**: Update `sam.py` to optionally route complex tasks through the `ReActOrchestrator`.

## Risk
**Failure Mode:** The model may get stuck in a "thought loop" where it repeatedly calls the same tool with the same input, or it may hallucinate tool names not in the registry.
**Mitigation:** Implement a "history buffer" that tracks previous `(action, observation)` pairs and injects them into the prompt to prevent redundant cycles.
**Confidence Score:** 8/10.

---

### Self-Correction
I must ensure that the `ReActOrchestrator` does not bypass my existing `_sleep()` and `_call_delay` logic. I will explicitly call `_sleep()` within the loop to maintain RPM compliance. I will also ensure the `max_steps` is set conservatively (e.g., 5) to prevent excessive token consumption during the initial testing phase.