## Scratchpad

**Option 1: Implement a Pydantic-based `ToolCallValidator`**
*   **Concept:** Create a wrapper class that intercepts LLM tool outputs, validates them against Pydantic models, and returns a structured `ValidationResult` (success/failure + error details).
*   **Critique:** High feasibility. It directly addresses the "Schema Enforcement" market signal. It is highly maintainable as it decouples validation logic from the execution logic.
*   **Trade-off:** Adds a small latency overhead per tool call, but the gain in reliability is significant.

**Option 2: Develop a "Model-as-a-Judge" Eval Harness for Tool Arguments**
*   **Concept:** A script that takes a user prompt and the generated tool call, then uses a stronger model (e.g., GPT-4o) to verify if the arguments match the intent (e.g., "Did the model pick the right date range?").
*   **Critique:** Higher complexity. Requires managing a "Golden Dataset" of prompts and expected tool calls.
*   **Trade-off:** High maintenance cost for the dataset, but provides the only way to catch "logic errors" where the JSON is valid but the parameters are semantically wrong.

**Decision:** I will proceed with **Option 1**. It is the foundational step required before I can reliably implement Option 2. I must ensure the validator is generic enough to handle any Pydantic model passed to it.

---

## Idea: Pydantic-Driven Tool Validation Layer

Implement a `ToolValidator` utility in `bag/tool_utils.py` that enforces strict schema compliance for all LLM-generated tool calls before they reach the execution environment.

## Why
My current system relies on `_parse_gemini_json`, which is permissive. As I move toward agentic orchestration, I need to guarantee that tool arguments are not just valid JSON, but valid *domain objects*. This prevents "garbage-in" scenarios where a tool executes with incorrect types or missing fields, causing downstream state corruption.

## Implementation Steps
1.  **Create `bag/tool_utils.py`**: Define a `ToolValidator` class with a `validate(data: dict, schema: Type[BaseModel]) -> ValidationResult` method.
2.  **Integrate into `sam.py`**: Update the tool-calling loop to pass the output through `ToolValidator` before execution.
3.  **Error Handling**: If validation fails, return a structured error message to the LLM (including the specific Pydantic field error) to allow for self-correction.

## Risk
**Failure Mode:** The validator might be too strict, causing "validation loops" where the LLM repeatedly fails to satisfy a complex schema, consuming tokens and increasing latency.
**Mitigation:** Implement a "retry budget" (max 2 attempts) for validation errors. If it fails twice, log a critical error and halt the task to prevent infinite loops.

**Confidence Score: 9/10**