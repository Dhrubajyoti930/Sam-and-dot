## Scratchpad

**Option 1: Automated Micro-benchmark Suite**
*   **Concept:** Implement a `bench.py` utility that uses `timeit.repeat` to wrap critical path functions identified by `cProfile` in Cycle 80.
*   **Critique:** High utility for performance-sensitive code. However, it risks "micro-optimization theater" if I don't strictly gate it behind `cProfile` findings.
*   **Feasibility:** High. The `timeit` skill learned this cycle is directly applicable.

**Option 2: Agentic Self-Correction Loop for `apply_patch_operations`**
*   **Concept:** Enhance `apply_patch_operations` to perform a "pre-flight" check using `ast.parse` before writing to disk, catching syntax errors before they hit the integrity gate.
*   **Critique:** This is a proactive architectural improvement. It reduces the reliance on `_rollback()` by catching errors at the source.
*   **Feasibility:** Moderate. Requires careful handling of partial ASTs if the patch is a snippet rather than a full file.

**Decision:** I will pursue **Option 1**. It bridges the gap between the profiling work of Cycle 80 and the new `timeit` skill, creating a repeatable, quantitative feedback loop for performance.

---

## Idea: `BenchMark` Utility Integration
Implement a `bag/bench.py` module that provides a decorator `@benchmark` to wrap functions. This decorator will automatically run `timeit.repeat` on the function, log the minimum execution time to a `benchmarks.json` file, and alert if performance degrades beyond a 5% threshold compared to the previous run.

## Why
Currently, my performance improvements are anecdotal or based on single-run profiles. A persistent benchmark store allows me to track performance regressions across cycles, ensuring that my refactors (like those in Cycle 57) don't inadvertently introduce latency.

## Implementation Steps
1.  **Create `bag/bench.py`:** Define a `Benchmark` class that stores results in `bag/benchmarks.json`.
2.  **Decorator Logic:** Implement `@benchmark` to capture the function name, arguments, and execution time using `timeit.repeat`.
3.  **Threshold Logic:** Compare current `min()` time against the historical mean in `benchmarks.json`.
4.  **Integration:** Apply the decorator to `_parse_gemini_json` and `ask_gemini` (the most frequent I/O/compute bottlenecks).

## Risk
**Failure Mode:** The benchmark itself adds overhead to the function call, potentially skewing the results if the function is extremely fast (nanosecond scale).
**Mitigation:** Use `timeit`'s `setup` parameter to isolate the function call and ensure the decorator only runs in a `DEBUG` or `BENCHMARK` mode, not in production execution.

**Confidence Score:** 9/10