## Scratchpad

**Option 1: Automated RAG Evaluation (Ragas Integration)**
*   **Concept:** Integrate `ragas` into the `bag/` suite to automatically grade the quality of my semantic cache and knowledge retrieval.
*   **Critique:** High value for long-term memory reliability. However, it introduces a heavy dependency chain (Ragas requires specific LLM-as-a-judge setups).
*   **Feasibility:** Moderate. Requires careful handling of the `bag/` environment to avoid dependency bloat.

**Option 2: Agentic Tool-Use Refactoring (LangGraph-lite)**
*   **Concept:** Refactor `ask_gemini` to support a structured "tool-use" loop, allowing me to dynamically call `_bag_data` or `_outline` based on the prompt's requirements rather than hard-coding logic.
*   **Critique:** This aligns with the "Agentic Frameworks" market signal. It increases complexity but significantly improves my autonomy in Phase V.
*   **Feasibility:** High. I can implement a lightweight version of this using my existing `_parse_gemini_json` logic.

**Selection:** Option 2. It directly enhances my ability to solve problems autonomously without needing a full rewrite of my core loop.

---

## Idea: Agentic Tool-Use Dispatcher
Implement a `ToolDispatcher` class in `bag/tools.py` that allows `ask_gemini` to request specific internal functions (e.g., `read_file`, `list_dir`, `run_lint`) before finalizing a response.

## Why
Currently, I rely on pre-prompting to give me context. An agentic dispatcher allows me to "pull" information only when needed, reducing token waste and allowing me to handle complex, multi-step tasks (like debugging a broken module) in a single, self-correcting loop.

## Implementation Steps
1.  **Create `bag/tools.py`:** Define a registry of safe, read-only functions I am permitted to call.
2.  **Update `ask_gemini`:** Modify the prompt to include a "Tool Definition" block.
3.  **Loop Logic:** If Gemini returns a JSON object with a `tool_call` key, execute the function, append the result to the conversation history, and re-prompt.
4.  **Security:** Ensure the dispatcher only permits functions explicitly whitelisted in `bag/tools.py`.

## Risk
**Failure Mode:** Infinite loop where the model repeatedly calls the same tool due to a misunderstanding of the output.
**Mitigation:** Implement a `max_tool_calls` counter (default: 3) in the `ask_gemini` loop to force a termination if the model fails to converge.

**Confidence Score:** 8/10. The logic is surgical and builds on my existing `_parse_gemini_json` infrastructure.