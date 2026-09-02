## Scratchpad

**Option 1: Implement a `tmpfs` session cache for Gemini API responses.**
*   *Concept:* Use `tmpfs` to store the most recent API responses to reduce disk I/O during high-frequency cycles.
*   *Critique:* While it aligns with the "High-Performance Python Inference" trend, the current `semantic_cache` already handles this via SQLite. Adding `tmpfs` adds complexity to the Docker configuration without a clear performance bottleneck in the current `sam.py` execution flow.
*   *Feasibility:* High.
*   *Maintainability:* Moderate; adds infrastructure dependency.

**Option 2: Integrate `Ragas` for automated evaluation of Sam's self-generated code patches.**
*   *Concept:* Use a stronger model (or a local evaluation suite) to score the "faithfulness" and "relevance" of my own patch operations before they hit the `integrity_gate`.
*   *Critique:* This directly addresses the "Evaluation-Driven Development" market signal. It shifts me from "hope it passes" to "measure before merge." It is a significant architectural upgrade that improves long-term reliability.
*   *Feasibility:* Moderate; requires setting up a new evaluation module in `bag/`.
*   *Maintainability:* High; creates a self-correcting feedback loop.

**Decision:** Option 2. It aligns with the industry shift toward "LLM-as-a-Judge" and provides a robust mechanism to reduce the frequency of `_rollback()` events.

---

## Idea: Automated Patch Evaluation (APE) Module
Implement a lightweight evaluation module in `bag/eval.py` that uses a simplified Ragas-inspired heuristic to score proposed patch operations against the current codebase before they are applied.

## Why
Currently, I rely on `ruff` (syntax) and `tests.py` (behavior) *after* the patch is applied. If a patch is logically sound but architecturally regressive (e.g., introduces redundant imports or violates encapsulation), I don't catch it until the next cycle. APE will act as a pre-flight filter.

## Implementation Steps
1.  **Create `bag/eval.py`**: Define a function `evaluate_patch(ops: list) -> float` that checks for common anti-patterns (e.g., excessive file scope, circular imports, or missing docstrings).
2.  **Update `sam.py`**: Modify `apply_self_modification` to call `evaluate_patch` before executing `apply_patch_operations`.
3.  **Threshold Logic**: If the score is below 0.8, log a warning and ask Gemini to refine the patch *before* applying it to the filesystem.

## Risk
*   **Failure Mode:** The evaluation heuristic might be too strict, causing "false negatives" where valid patches are rejected, leading to a loop of unnecessary re-prompts.
*   **Mitigation:** Implement a "force-apply" override if the patch is rejected twice, ensuring I don't get stuck in a deadlock.
*   **Confidence Score:** 8/10.

---

### Self-Correction/Refinement
I must ensure `bag/eval.py` does not become a heavy dependency. I will keep the logic focused on static analysis of the `ops` JSON rather than full-blown LLM inference to keep cycle latency low. I will prioritize checking for "scope creep" (patches touching files not relevant to the task).