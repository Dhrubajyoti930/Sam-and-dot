## Scratchpad

**Option 1: KV-Cache Quantization Integration**
*   **Concept:** Implement INT8 KV-cache quantization for the local inference engine.
*   **Critique:** High impact on memory efficiency for long-context tasks. However, it requires deep integration with the underlying inference kernel (e.g., `vLLM` or `llama.cpp` bindings).
*   **Feasibility:** Moderate. Requires careful handling of the `PagedAttention` buffers.
*   **Maintainability:** High, as it reduces OOM risks during complex reasoning cycles.

**Option 2: Evaluation-Driven Development (EvalOps) Pipeline**
*   **Concept:** Integrate `Ragas` to automatically score the quality of my own self-generated code plans and documentation against a set of "golden" benchmarks.
*   **Critique:** Directly addresses the "vibes-based" testing weakness. It creates a feedback loop that forces me to be more precise.
*   **Feasibility:** High. I can build a small `eval_bench.py` in `workshop_bench/` that runs after `behaviour_check()`.
*   **Maintainability:** Excellent. It provides objective data for my 1% growth metric.

**Decision:** Option 2 is more aligned with my current need for rigorous self-assessment and long-term stability.

---

## Idea: EvalOps Integration via Ragas-lite Benchmarking

Implement a lightweight evaluation harness (`workshop_bench/eval_harness.py`) that uses a small, curated set of "Golden Prompts" and expected output schemas to score my planning phases.

## Why
My current `behaviour_check()` only tests if the code *runs*. It does not test if the *logic* or *reasoning* behind a patch is optimal. By introducing an evaluation layer, I can measure "reasoning drift" and ensure that my self-modifications are actually improving the system's utility rather than just maintaining syntax.

## Implementation Steps
1.  **Create `workshop_bench/eval_harness.py`**: Define a `GoldenBenchmark` class that stores input prompts and expected Pydantic-validated output structures.
2.  **Update `sam.py`**: Modify `run_cycle()` to trigger `eval_harness.py` after `behaviour_check()` passes.
3.  **Logging**: Store evaluation scores in `bag/eval_metrics.json` to track performance over cycles.
4.  **Feedback Loop**: If a score falls below a threshold (e.g., 0.8), trigger a "Refinement Phase" where I re-evaluate the last patch.

## Risk
**Failure Mode:** The evaluation harness itself becomes a source of technical debt or creates "false negatives" where a valid, creative architectural improvement is penalized for deviating from the "golden" path.
**Mitigation:** Keep the benchmark set small and focused on structural integrity and schema compliance rather than subjective "style." Use a "soft-fail" mechanism where low scores trigger a log warning rather than an immediate rollback.

**Confidence Score:** 8/10