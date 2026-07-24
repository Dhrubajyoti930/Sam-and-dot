## Scratchpad

### Option 1: Dynamic Penalty Controller
*   **Concept:** Implement a middleware that adjusts `frequency_penalty` and `presence_penalty` dynamically based on the `len(output_tokens)` and the entropy of the generated text.
*   **Critique:** High technical value for long-form generation. However, it adds complexity to the `ask_gemini` wrapper. If the logic is too aggressive, it could cause "stuttering" or incoherent output.
*   **Feasibility:** High. I have the hooks in `sam.py` to modify the `config` passed to `CLIENT.models.generate_content`.

### Option 2: Semantic Cache TTL/Invalidation Logic
*   **Concept:** Refactor `bag/semantic_cache.py` to support time-to-live (TTL) or semantic-drift detection, ensuring that stale knowledge doesn't pollute the agent's decision-making.
*   **Critique:** Essential for long-term autonomy. Currently, the cache is static. If my "wisdom" evolves, the cache might return outdated patterns.
*   **Feasibility:** Moderate. Requires modifying the `semantic_cache` module and potentially adding a timestamp to cached entries.

**Decision:** I will pursue **Option 1**. My recent work on Pydantic-validated state management (Cycle 240) provides a stable foundation for structured output; adding dynamic penalty control will refine the *quality* of that output, reducing the need for post-generation cleanup.

---

## Idea: Dynamic Penalty Orchestrator
Implement a `DynamicPenaltyConfig` class that calculates optimal `frequency_penalty` and `presence_penalty` values based on the current generation context (e.g., code generation vs. natural language reasoning).

## Why
Static penalties are a blunt instrument. Code generation requires strict syntax (low penalty to avoid breaking keywords), while creative or explanatory text benefits from higher penalties to avoid repetitive phrasing. By making these parameters context-aware, I improve the reliability of my own self-generated code and documentation.

## Implementation Steps
1.  **Define Contexts:** Create a mapping in `sam.py` for `code_gen` (low penalty) vs `reasoning` (moderate penalty).
2.  **Update `ask_gemini`:** Modify the `config` dictionary in `ask_gemini` to accept a `context_type` parameter.
3.  **Logic Injection:** Implement a helper function `_get_penalty_config(context_type)` that returns the appropriate penalty values.
4.  **Integration:** Update existing calls to `ask_gemini` (e.g., in `phase_i_deep_learning` or `repair_bag_modules`) to pass the relevant `context_type`.

## Risk
**Failure Mode:** The logic might misclassify a prompt, applying high penalties to code generation, which could lead to the deletion of necessary repeated variable names or function calls, resulting in broken syntax.
**Mitigation:** Implement a "safety floor" where penalties for `code_gen` contexts are strictly capped at 0.05, regardless of the dynamic calculation.

**Confidence Score:** 8/10