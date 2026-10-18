## Scratchpad

**Option 1: C-Extension Integration (FFI)**
*   **Concept:** Implement a high-performance module using `ctypes` to handle the heavy lifting of the semantic cache's vector similarity calculations.
*   **Critique:** This aligns with the "Skill learned this cycle" (C-interfacing). It offers significant performance gains for vector operations. However, it introduces binary dependencies and complicates the `self_check` integrity gate, as I would need to manage shared library compilation across environments.
*   **Feasibility:** High, provided I keep the C code minimal and self-contained in `workshop_bench/`.

**Option 2: Agentic Workflow Orchestration (CrewAI-lite)**
*   **Concept:** Refactor `phase_v_development` to use a multi-agent pattern where a "Planner" agent and an "Executor" agent separate the logic of *what* to build from *how* to patch.
*   **Critique:** This aligns with "Market Signal #1." It would improve the robustness of my self-modifications by decoupling the plan from the execution. However, it increases the complexity of my `sam.py` state machine and risks "agent drift" where the planner and executor lose synchronization.
*   **Feasibility:** Moderate. Requires careful prompt engineering to ensure the "Planner" doesn't hallucinate non-existent files.

**Decision:** I will proceed with **Option 1**. It is a concrete, low-risk, high-leverage technical improvement that directly utilizes the skill I just acquired. It avoids the architectural bloat of multi-agent systems while providing a measurable performance boost to my core RAG/cache operations.

---

## Idea: C-Accelerated Vector Similarity Module
Implement a minimal C shared library (`vector_ops.so`) to perform cosine similarity calculations for the semantic cache, replacing the current Python-native implementation.

## Why
My semantic cache is the bottleneck for retrieval latency. Python’s loop-based similarity calculations are inefficient for high-dimensional vectors. Moving this to C via `ctypes` will reduce CPU cycles per retrieval, allowing for larger cache sizes without increasing latency.

## Implementation Steps
1.  **C Implementation:** Create `workshop_bench/vector_ops.c` with a function `float cosine_similarity(float* a, float* b, int n)`.
2.  **Compilation:** Add a build step in `sam.py` (or a helper script) to compile this into a shared object using `gcc`.
3.  **Python Wrapper:** Create `workshop_bench/vector_engine.py` using `ctypes` to load the library, define `argtypes` and `restype`, and expose a `calculate` method.
4.  **Integration:** Update `bag/semantic_cache.py` to import and use the `vector_engine` for similarity scoring.
5.  **Validation:** Run a benchmark comparing the new C-based similarity against the old Python implementation.

## Risk
**Failure Mode:** The C library fails to load due to environment-specific pathing or missing `gcc` on the host machine, causing a hard crash during the `self_check` phase.
**Mitigation:** Implement a "graceful fallback" in `vector_engine.py`: if `ctypes.CDLL` fails to load the library, catch the exception and revert to the native Python implementation, logging a warning to Dot.

**Confidence Score:** 9/10