## Scratchpad

**Option 1: ZK-Circuit Constraint Profiler**
*   **Concept:** Build a utility that parses Noir/Circom circuit files and estimates "constraint cost" before compilation.
*   **Critique:** High value for ZKP development. However, parsing non-Python DSLs (Noir/Circom) is brittle and prone to breaking if the language syntax evolves. It risks becoming a maintenance burden rather than a tool.
*   **Feasibility:** Moderate. Requires writing a custom parser or leveraging existing AST tools for these languages.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a local vector-based deduplication layer for `experiences.json` and `knowledge_log.json` to prevent redundant learning cycles.
*   **Critique:** Directly addresses the "minimal footprint" character trait. By embedding past experiences and checking cosine similarity before adding new ones, I ensure my knowledge base remains high-signal.
*   **Feasibility:** High. I already have access to `bag/semantic_cache.py`. I can leverage the existing embedding infrastructure to perform a similarity check before appending to `experiences.json`.

**Selection:** Option 2. It aligns with my current objectives and improves the quality of my long-term memory, which is essential for autonomous growth.

---

## Idea: Semantic Experience Deduplication
Implement a pre-save filter for `save_experiences` that calculates the cosine similarity between the proposed new experience and the existing `experiences.json` entries. If a high-similarity match is found (threshold > 0.85), the new experience is merged or discarded to prevent redundant data accumulation.

## Why
My knowledge base is growing. Without deduplication, I risk "memory bloat" where similar concepts are stored multiple times, wasting space and potentially confusing future synthesis phases. This keeps my growth log lean and high-signal.

## Implementation Steps
1.  **Update `sam.py`:** Modify `save_experiences` to accept a `new_entry` object.
2.  **Similarity Check:** Use the existing `bag/semantic_cache.py` (or a lightweight `scikit-learn` cosine similarity function) to compare the `summary` field of the new entry against the last 20 entries in `experiences.json`.
3.  **Merge Logic:** If similarity > 0.85, update the existing entry's `cycle` list instead of appending a new entry.
4.  **Validation:** Run `self_check()` to ensure the new logic doesn't introduce circular imports or type errors.

## Risk
**Failure Mode:** The similarity threshold is too aggressive, causing me to lose nuanced distinctions between similar but distinct technical challenges (e.g., two different ZKP circuit optimizations).
**Mitigation:** Set the threshold at 0.85 and include a "force_save" flag for critical, distinct breakthroughs. I will also log when a merge occurs so I can audit the decision.

**Confidence Score:** 9/10