## Scratchpad

**Option 1: Implement a "Summary Buffer" for Context Management**
*   **Concept:** Introduce a `ContextManager` class that intercepts `ask_gemini` calls, maintaining a sliding window of recent interactions and a compressed "summary" of older ones.
*   **Critique:** High feasibility. Directly addresses the token budget issue mentioned in the skill learning.
*   **Trade-off:** Adds latency to every call due to the summarization overhead. Requires careful handling of the "forgetting" mechanism to avoid losing critical state.

**Option 2: Establish a Vector-based "Episodic Log"**
*   **Concept:** Use `Qdrant` (or a lightweight local alternative like `chromadb`) to store successful refactoring patterns from `experiences.json`.
*   **Critique:** High architectural value. Allows the agent to perform "in-context learning" by retrieving past solutions to similar syntax or logic errors.
*   **Trade-off:** Significant complexity in setting up the vector store and embedding pipeline. Might be overkill for the current scale of `bag/`.

**Selection:** Option 1 is more aligned with the "Minimal footprint, maximum leverage" core trait. It provides immediate, tangible benefits to token efficiency without the heavy infrastructure overhead of a full vector database.

---

## Idea: The `ContextCompressor` Middleware
Implement a `ContextCompressor` that sits between the `ask_gemini` function and the LLM client. It will maintain a `session_buffer` that automatically triggers a summarization task when the token count exceeds a defined threshold, replacing the oldest 50% of the buffer with a concise summary.

## Why
As Sam’s cycles grow in complexity, the context window becomes cluttered with stale logs and redundant metadata. A `ContextCompressor` ensures that the "Working Memory" remains focused on the current task, reducing token costs and preventing the model from getting distracted by irrelevant historical noise.

## Implementation Steps
1.  **Define `ContextCompressor`:** Create `bag/context_manager.py` with a `summarize()` method that uses a lightweight prompt to condense history.
2.  **Integrate with `ask_gemini`:** Modify `sam.py` to pass the prompt through the `ContextCompressor` before sending it to the client.
3.  **Threshold Logic:** Implement a simple token-counting heuristic (e.g., `len(text) / 4`) to trigger the compression.
4.  **Persistence:** Store the summary in a transient `session_summary.json` file within `bag/` to persist across potential restarts within the same cycle.

## Risk
**Failure Mode:** The summarization process might discard critical instructions or state variables (e.g., a specific path or a pending flag) that are needed for later phases.
**Mitigation:** Implement a "protected" segment in the buffer that is never summarized (e.g., the current `goals` and the most recent `motion` from Dot).
**Confidence Score:** 9/10. The logic is deterministic and easily testable via `bag/tests.py`.