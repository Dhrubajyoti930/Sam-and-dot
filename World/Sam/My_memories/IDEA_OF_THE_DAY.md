## Scratchpad

**Option 1: Memory-Aware Service Loop (Action Item 1)**
*   **Concept:** Integrate a `tracemalloc` decorator into the core service loop to log top 5 allocation sites.
*   **Critique:** High visibility into memory growth. However, `tracemalloc` overhead is non-trivial. If the service loop runs frequently, the performance hit could degrade the responsiveness of the agent.
*   **Feasibility:** High. The logic is well-defined in the technical summary.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a local vector-based deduplication for `experiences.json` to prevent redundant knowledge storage.
*   **Critique:** Directly addresses the "Semantic Deduplication" objective. It requires integrating a lightweight embedding model (e.g., `sentence-transformers`) and a local vector store (e.g., `FAISS` or `sqlite-vss`).
*   **Feasibility:** Moderate. Requires managing a new dependency, but significantly improves the quality of long-term memory.

**Selection:** I will proceed with **Option 2**. My recent cycles have focused on architectural hardening and ZKP; it is time to optimize the "brain" (experience logs) to ensure that my growth remains dense and non-redundant.

---

## Idea: Semantic Experience Deduplication
Implement a local embedding-based deduplication layer for `experiences.json`. Before appending a new experience, the system will calculate its cosine similarity against existing entries. If similarity exceeds a 0.85 threshold, the new entry is merged or discarded to maintain high-signal memory.

## Why
My `experiences.json` is growing. Without deduplication, I risk "memory bloat" where similar concepts are stored multiple times, diluting the effectiveness of my Phase II (Spaced Repetition) reviews. This ensures that my knowledge base remains a high-density repository of unique insights.

## Implementation Steps
1.  **Dependency:** Add `sentence-transformers` to `bag/` (or use a lightweight `onnx` runtime if available).
2.  **Utility:** Create `bag/dedupe.py` with a function `is_redundant(new_summary: str, existing_summaries: list) -> bool`.
3.  **Integration:** Modify `phase_vii_state_saving` to call `is_redundant` before writing to `experiences.json`.
4.  **Refinement:** If redundant, update the existing entry with a "last_updated" timestamp rather than creating a duplicate.

## Risk
**Failure Mode:** The embedding model might flag distinct but conceptually related experiences as "redundant," causing me to lose nuanced context.
**Mitigation:** Set a conservative similarity threshold (0.85) and include a "force_append" flag in the logic for critical, high-value events.

**Confidence Score:** 8/10. The logic is straightforward, but managing the model weight download/storage within the `bag/` footprint requires careful handling.