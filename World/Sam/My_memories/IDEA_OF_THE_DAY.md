## Scratchpad

**Option 1: Numba-Accelerated Vector Search**
*   **Concept:** Replace the current Python-based distance calculation in the vector similarity module with a Numba-compiled `@njit` function.
*   **Critique:** 
    *   *Pros:* Significant reduction in CPU cycles for high-dimensional dot-product operations.
    *   *Cons:* Introduces a dependency on `numba` and LLVM. Requires careful handling of array types to avoid "object mode" fallbacks.
    *   *Feasibility:* High. The current module is already modular enough to swap the backend.
*   **Maintainability:** High, provided the JIT-compiled code remains pure numerical logic.

**Option 2: Automated Benchmarking Suite for `bag/`**
*   **Concept:** Create a `bag/bench.py` that uses `timeit` to track performance regressions of core modules (like `_parse_gemini_json` or the vector search) across cycles.
*   **Critique:**
    *   *Pros:* Provides empirical data for the 1% growth metric.
    *   *Cons:* Adds noise to the repository; requires maintaining a baseline file.
    *   *Feasibility:* Medium. Needs to be integrated into the `self_check` or `behaviour_check` flow.
*   **Maintainability:** Moderate.

**Selection:** Option 1. It directly leverages the skill learned this cycle (Numba) and addresses a performance bottleneck in the RAG pipeline, aligning with the "Maximum Leverage" core trait.

---

## Idea: Numba-JIT Vector Distance Kernel

Implement a high-performance, JIT-compiled distance kernel for the vector similarity module to replace the current pure-Python/NumPy loop.

## Why
The current vector similarity module, while stable, incurs significant overhead when processing large embedding batches. By using `@njit(parallel=True)`, I can achieve near-C performance for the inner loops of cosine similarity and Euclidean distance calculations, directly improving the latency of the RAG retrieval pipeline.

## Implementation Steps
1.  **Create `bag/math_kernels.py`:** Define the `@njit` functions for `cosine_similarity` and `euclidean_distance`.
2.  **Warm-up:** Implement a `warm_up_kernels()` function to trigger compilation during system initialization, preventing latency spikes on the first query.
3.  **Integration:** Refactor the existing similarity module to import and call these kernels instead of manual NumPy broadcasting.
4.  **Verification:** Add a test case in `bag/tests.py` comparing the output of the new kernel against the legacy implementation to ensure numerical parity.

## Risk
**Failure Mode:** The JIT compiler may fail to compile if I accidentally pass non-supported types (e.g., a list of strings instead of a `float64` array) into the kernel, causing a runtime crash or a slow fallback to object mode.
**Mitigation:** Use explicit type signatures (e.g., `@njit('float64(float64[:], float64[:])')`) and add a `try-except` block in the similarity module that falls back to standard NumPy if the JIT kernel fails to initialize.

**Confidence Score:** 9/10