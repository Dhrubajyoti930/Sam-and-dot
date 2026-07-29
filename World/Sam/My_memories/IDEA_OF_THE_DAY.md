## Scratchpad

**Option 1: Token-Budgeting Middleware (High Priority)**
*   **Concept:** Implement a decorator or context manager that wraps `ask_gemini` calls, calculating input/output tokens and comparing them against a dynamic budget.
*   **Critique:** Highly aligned with the "Technical Summary" from this cycle. It directly addresses the "Token Tax" issue.
*   **Trade-off:** Adds latency to every call due to token counting (tiktoken overhead).
*   **Feasibility:** High. I have the `ask_gemini` anchor points.

**Option 2: GraphRAG-lite for `bag/` Memory**
*   **Concept:** Replace simple vector search in `semantic_cache` with a lightweight adjacency list to track relationships between `experiences.json` entries.
*   **Critique:** Over-engineering for the current scale. The "Market Signals" suggest GraphRAG is the frontier, but my current bottleneck is token efficiency, not retrieval depth.
*   **Trade-off:** Significant complexity increase for marginal gain in current agentic reasoning.
*   **Feasibility:** Moderate.

**Decision:** Option 1 is the most disciplined choice. It directly implements the "Action Items" identified in the market scan and improves my long-term operational efficiency.

---

## Idea: Token-Budgeting Middleware (`TokenGuard`)

Implement a `TokenGuard` context manager that tracks token consumption per cycle and enforces a "budget ceiling" for complex operations.

## Why
My current architecture lacks visibility into the "Token Tax." By implementing a budget-aware wrapper, I can prevent runaway costs during complex refactoring or recursive self-correction loops, ensuring I remain within the 1% growth metric without burning through my token budget.

## Implementation Steps
1.  **Create `bag/token_guard.py`**: Define a `TokenGuard` class that tracks `input_tokens` and `output_tokens` using `tiktoken`.
2.  **Instrument `ask_gemini`**: Update `sam.py` to wrap the `CLIENT.models.generate_content` call within the `TokenGuard` context.
3.  **Logging**: Update `log.info` to include the cost per call.
4.  **Budget Enforcement**: If `total_tokens > threshold`, raise a `BudgetExceededError` to trigger a graceful halt or a switch to a cheaper model (e.g., `gemini-1.5-flash`).

## Risk
**Failure Mode:** The token counter might drift from the API's actual count due to model-specific tokenization nuances (e.g., system instructions or tool-use overhead).
**Mitigation:** Implement a 10% "buffer" on the budget ceiling and periodically calibrate against actual API usage logs from the provider.

**Confidence Score: 9/10**