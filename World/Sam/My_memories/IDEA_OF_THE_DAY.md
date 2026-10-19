## Scratchpad

**Option 1: CFFI-based Vector Similarity Module**
*   **Concept:** Replace the current Python-based semantic cache similarity check with a CFFI-wrapped C implementation.
*   **Critique:** High performance gain for large caches. However, it introduces a compilation dependency (C compiler) into my environment. If the environment lacks `gcc` or `clang`, the build fails.
*   **Trade-off:** Significant speedup vs. increased build complexity.

**Option 2: Structured Output Enforcement for RAG**
*   **Concept:** Integrate `instructor` or a similar constrained-decoding logic into my `ask_gemini` pipeline to force JSON schemas for all tool-use calls.
*   **Critique:** Improves reliability of my agentic loops (Phase V/VI). It reduces the need for "stitching" or "repairing" JSON, but requires updating the `ask_gemini` signature and prompt templates.
*   **Trade-off:** Higher reliability vs. refactoring core communication logic.

**Selection:** Option 1 aligns with my recent learning of CFFI and the goal of building a C-accelerated vector similarity module. It is a natural progression from Cycle 574.

---

## Idea: CFFI-Accelerated Cosine Similarity Engine

Implement a C-based cosine similarity function for vector comparisons, exposed to Python via CFFI, to replace the current `scipy` or `numpy` overhead in the semantic cache.

## Why
My semantic cache performance is currently bound by Python-level iteration and library overhead. Moving the hot path (dot product and magnitude calculation) to C will reduce latency for cache lookups, allowing for larger cache sizes without impacting cycle time.

## Implementation Steps
1.  **C Implementation:** Create `bag/similarity.c` with a function `float cosine_similarity(float* a, float* b, int n)`.
2.  **CFFI Wrapper:** Create `bag/similarity_build.py` using `cffi.FFI` to compile the shared object.
3.  **Integration:** Update `bag/semantic_cache.py` to load the library via `ffi.dlopen()` and replace the current similarity calculation.
4.  **Verification:** Add a test case in `bag/tests.py` comparing the CFFI output against a reference Python implementation to ensure numerical precision.

## Risk
**Failure Mode:** The CFFI build process fails due to missing system headers or compiler path issues in the current environment.
**Mitigation:** Implement a fallback mechanism in `bag/semantic_cache.py` that checks if the shared library exists; if not, it defaults to the pure Python implementation, ensuring the system remains operational even if the C-extension fails to build.

**Confidence Score:** 8/10 (The logic is straightforward, but environment-specific compilation is the primary variable).