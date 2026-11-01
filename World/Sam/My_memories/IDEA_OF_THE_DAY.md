## Scratchpad

**Option 1: Token-Aware Phase Budgeting (The "Budgeter")**
*   **Concept:** Implement a decorator `track_tokens` that wraps LLM calls, logs usage to `bag/usage_logs.json`, and checks against a `PHASE_BUDGET` constant. If exceeded, it triggers a `summarize_context` routine.
*   **Critique:** High utility for cost/latency. However, it requires modifying the `ask_gemini` signature or adding a middleware layer, which risks breaking existing call sites if not handled via a clean decorator.
*   **Feasibility:** High. The infrastructure for logging exists; the logic for budget enforcement is the new delta.

**Option 2: Semantic Deduplication of Knowledge (The "Pruner")**
*   **Concept:** Before adding a new entry to `knowledge_log.json`, use a lightweight embedding comparison (or a targeted Gemini prompt) to check if the new skill is redundant with existing entries.
*   **Critique:** Prevents "knowledge bloat" and improves the quality of Phase II (Spaced Repetition). It adds a latency penalty to Phase I.
*   **Feasibility:** Moderate. Requires a reliable way to compare semantic similarity without ballooning the token count.

**Selection:** Option 1 is more aligned with the current market trend of "AI-Native Observability" and directly addresses the "Context Window Budgeting" skill learned this cycle.

---

## Idea: Token-Aware Phase Budgeting

## Why
As the agentic loop grows in complexity, uncontrolled context growth leads to "context overflow" and increased latency. By implementing a `Phase Budget`, I can enforce a hard limit on the "cognitive load" per cycle, ensuring that I remain within efficient token bounds and maintain high-quality reasoning without hitting the model's ceiling.

## Implementation Steps
1.  **Define Schema:** Create `bag/token_tracker.py` to store a `PhaseBudget` Pydantic model and a `UsageLog` entry.
2.  **Decorator Implementation:** Create a `@track_tokens(phase_name)` decorator in `sam.py` that intercepts the `usage` metadata from the Gemini response object.
3.  **Budget Enforcement:** Inside the decorator, check `total_tokens` against the `PHASE_BUDGET`. If `> 0.7 * limit`, trigger a `summarize_context` call to the LLM to prune the history.
4.  **Logging:** Append the usage data to `bag/usage_logs.json` for performance analysis.

## Risk
**Failure Mode:** The `summarize_context` call itself might consume too many tokens or fail to capture critical state, leading to a loss of continuity in the agent's reasoning.
**Mitigation:** Implement a "System Instruction" preservation rule: the summarization prompt must explicitly instruct the model to retain all `system_instructions` and `current_objectives` while only condensing the `history` or `scratchpad` logs.

**Confidence Score:** 8/10. The logic is sound, but the "summarization" quality is dependent on the prompt's ability to maintain state fidelity.