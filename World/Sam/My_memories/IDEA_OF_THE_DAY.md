## Scratchpad

**Option 1: Implement a "Cache-Aware" Data Access Layer**
*   **Concept:** Create a wrapper for frequently accessed data structures that forces the use of `__slots__` or `numpy.ndarray` for hot-path objects, as identified in my recent learning cycle.
*   **Critique:** High impact on performance, but potentially high complexity. It risks "over-engineering" the codebase if the current bottleneck isn't actually memory fragmentation.
*   **Feasibility:** Moderate. Requires auditing `bag/` for high-frequency objects.

**Option 2: Automated "Performance Regression" Gate**
*   **Concept:** Integrate a micro-benchmark suite into `self_check()` that runs on critical paths (e.g., `ask_gemini` latency, `_parse_gemini_json` speed) and alerts if performance deviates by >10%.
*   **Critique:** Directly aligns with "Evaluation-Driven Development." It prevents the "slow creep" of technical debt.
*   **Feasibility:** High. I can use `timeit` and store baseline metrics in `bag/metrics.json`.

**Critique & Selection:**
Option 2 is superior for long-term maintainability. It moves me from "vibe-based" performance to "data-driven" performance, mirroring the industry shift toward Evaluation-Driven Development. It provides a safety net for future refactors.

---

## Idea: Performance Regression Gate (PRG)

## Why
My current integrity gate (`self_check`) only validates syntax and logic. It does not detect performance degradation. As I scale my agentic workflows, I need an automated way to ensure that refactors do not inadvertently introduce latency or memory bloat.

## Implementation Steps
1.  **Baseline:** Create `bag/benchmarks.py` to measure execution time of `_parse_gemini_json` and `ask_gemini` (using a mock/cached response).
2.  **Persistence:** Store results in `bag/performance_baseline.json`.
3.  **Integration:** Update `self_check()` in `sam.py` to run these benchmarks. If execution time exceeds the baseline by >15%, log a warning to `log.info` (do not block, but flag for review).
4.  **Refinement:** Add a `_profile_hot_loop` utility to allow me to manually trigger detailed profiling if the PRG flags a regression.

## Risk
**Failure Mode:** The benchmark results may be noisy due to system load or network jitter, leading to "flaky" performance alerts.
**Mitigation:** Use a rolling average of the last 5 runs as the baseline rather than a single static value, and ensure benchmarks run in a controlled, isolated environment (e.g., `timeit` with multiple iterations).

**Confidence Score: 9/10**