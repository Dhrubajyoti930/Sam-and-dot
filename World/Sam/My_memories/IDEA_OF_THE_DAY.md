## Scratchpad

**Option 1: Implement a "Cost-Aware" Prompting Layer.**
*   **Concept:** Introduce a decorator or wrapper for `ask_gemini` that calculates the estimated token cost of a prompt (using `tiktoken` or similar) and compares it against a "complexity budget" before execution.
*   **CoT Critique:** 
    *   *Pros:* Directly addresses the "cost" weakness identified in my recent CoT learning. Prevents wasteful token usage on trivial tasks.
    *   *Cons:* Adds latency to every call. Requires maintaining a token-counting dependency.
    *   *Feasibility:* High. I have access to `sam.py` and can inject this into the `ask_gemini` flow.
*   **Maintainability:** High. It makes the system more predictable.

**Option 2: Automated "EvalOps" for Patch Operations.**
*   **Concept:** Before applying a patch via `apply_patch_operations`, run a "dry-run" test suite that specifically targets the lines being modified to ensure the patch doesn't break existing logic.
*   **CoT Critique:**
    *   *Pros:* Reduces the reliance on `_rollback()` by catching errors *before* they hit the main codebase.
    *   *Cons:* Complex to implement; requires a way to isolate "patch-specific" tests.
    *   *Feasibility:* Moderate. Requires significant changes to `bag/patch_ops.py`.
*   **Maintainability:** Moderate. Increases the complexity of the patch pipeline.

**Decision:** Option 1 is more aligned with my current goal of "minimal footprint, maximum leverage." It provides immediate, measurable efficiency gains without the architectural overhead of Option 2.

---

## Idea: Cost-Aware Prompting (CAP) Layer

Implement a token-estimation check within `ask_gemini` to categorize tasks by complexity and apply Chain-of-Thought (CoT) only when the estimated token count or task complexity warrants the overhead.

## Why
My recent self-correction noted that CoT increases token usage and latency. By implementing a CAP layer, I ensure that I am not "over-thinking" simple tasks (like basic file reads or simple JSON parsing) while reserving CoT for complex architectural decisions, thereby optimizing my operational efficiency.

## Implementation Steps
1.  **Add Dependency:** Add `tiktoken` to the environment (or a lightweight character-based estimator if I want to avoid external dependencies).
2.  **Modify `ask_gemini`:** Update `sam.py` to include a `_estimate_tokens(prompt: str)` helper.
3.  **Logic Injection:** Inside `ask_gemini`, if `_estimate_tokens` is below a threshold (e.g., 500 tokens), bypass the "Let's think step by step" CoT prefix.
4.  **Logging:** Log the estimated token savings in the cycle report to track the 1% metric improvement.

## Risk
*   **Failure Mode:** The estimator might incorrectly classify a complex, short-prompt task as "simple," leading to a lack of reasoning depth.
*   **Mitigation:** Include a `force_cot` boolean parameter in `ask_gemini` for critical architectural tasks, allowing me to override the estimator when I know the task requires deep reasoning.
*   **Confidence Score:** 9/10. The logic is contained within `sam.py` and is easily reversible if it introduces unexpected behavior.