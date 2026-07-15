## Scratchpad

**Option 1: Dynamic Tool Registry Injection**
*   **Concept:** Instead of loading all tools into the context window, implement a semantic search over tool descriptions to inject only the top-k relevant tools for the current task.
*   **Critique:** High impact on token efficiency and model performance. However, it introduces complexity in the `ask_gemini` loop. If the semantic search fails to retrieve a critical tool, the agent stalls.
*   **Feasibility:** High, given the existing `semantic_cache` infrastructure.

**Option 2: Tool Execution Traceback Injection**
*   **Concept:** Wrap all tool calls in a `try-except` block that captures the full traceback and appends it to the next prompt if the tool fails, allowing the model to self-correct.
*   **Critique:** Directly addresses the "Execution Loop" weakness identified in my self-correction. It is a surgical, low-risk change that significantly increases system robustness.
*   **Feasibility:** Very high; requires minimal changes to the execution wrapper.

**Decision:** Option 2 is the superior choice for this cycle. It aligns with the "system-centric" engineering shift and directly improves the reliability of my autonomous workflows without the overhead of a dynamic registry.

---

## Idea: Automated Tool-Failure Self-Correction Loop

Implement a standardized `execute_with_retry` wrapper for all tool calls that catches exceptions, formats the traceback, and injects it into the subsequent `ask_gemini` turn as a "Correction Context."

## Why
Currently, if a tool fails (e.g., a malformed argument or a missing file), the system logs the error, but the model remains unaware of the specific failure reason. This forces a manual intervention or a blind retry. By feeding the traceback back to the model, I enable the model to reason about its own syntax or logic errors and apply a fix in the next turn.

## Implementation Steps
1.  **Modify `bag/patch_ops.py` (or a new `bag/tool_executor.py`):** Create a wrapper function that executes a tool and returns a `(result, error_traceback)` tuple.
2.  **Update `ask_gemini` logic:** If a tool call is detected in the response, the system will attempt execution. If it fails, the system will automatically append the traceback to the `contents` of the next `ask_gemini` call with a system instruction: "The previous tool execution failed. Analyze the traceback and correct your approach."
3.  **Validation:** Add a test case in `bag/tests.py` that intentionally triggers a tool failure to verify the model receives the traceback and attempts a correction.

## Risk
**Failure Mode:** The model might enter an infinite loop of "hallucinated corrections" if the error is environmental (e.g., a permission issue) rather than logical.
**Mitigation:** Implement a `max_retries` counter (e.g., 2) in the execution loop. If the error persists after two attempts, the system halts and alerts Dot.

**Confidence Score:** 9/10