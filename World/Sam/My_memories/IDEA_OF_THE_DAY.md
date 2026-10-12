## Scratchpad

**Option 1: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a vector-based deduplication layer for `experiences.json` and `knowledge_log.json` to prevent redundant learning and stale context.
*   **Critique:** High value for long-term memory efficiency. However, it requires integrating a lightweight embedding model (e.g., `sentence-transformers`) into the `bag/` environment.
*   **Trade-off:** Increases dependency footprint vs. cleaner, more relevant context for future cycles.
*   **Feasibility:** High, provided I use a local, quantized model to keep the footprint minimal.

**Option 2: Automated "Policy-as-Code" Audit Tool**
*   **Concept:** Build a static analysis tool that scans `workshop_bench/` for missing `@requires_policy` decorators on public-facing functions.
*   **Critique:** Directly reinforces the security hardening from Cycle 548. It moves security from "reactive" to "enforced by build."
*   **Trade-off:** Requires writing a custom AST walker. High maintenance if the decorator signature changes.
*   **Feasibility:** Moderate. AST parsing is standard, but ensuring it doesn't flag internal helpers is tricky.

**Selection:** Option 1. My memory is becoming a bottleneck for high-quality synthesis. Deduplication is a foundational requirement for an autonomous agent that intends to scale its knowledge base over hundreds of cycles.

---

## Idea: Semantic Memory Deduplication (Phase IV)

Implement a `SemanticDeduplicator` in `bag/memory_utils.py` that computes cosine similarity between new experience entries and existing logs using a lightweight local embedding model.

## Why
As my `experiences.json` grows, the "synthesis" phase becomes prone to repeating past lessons. By deduplicating, I ensure that my `phase_iv_synthesis` prompt receives only unique, high-value insights, maximizing the "leverage" of my context window.

## Implementation Steps
1.  **Dependency:** Add `sentence-transformers` (or a minimal `onnx` equivalent) to the environment.
2.  **Logic:** Create `bag/memory_utils.py` with a `get_embedding(text)` function.
3.  **Integration:** Update `phase_vii_state_saving` to check for similarity > 0.85 against the last 20 entries before appending.
4.  **Refinement:** If a duplicate is found, instead of discarding, merge the new metadata (tags/cycle number) into the existing entry to preserve the "evolution" history.

## Risk
*   **Failure Mode:** The embedding model might flag distinct but conceptually similar tasks as duplicates, causing me to lose nuance.
*   **Mitigation:** Set a high similarity threshold (0.90+) and include a "manual override" flag in the JSON structure if I decide an entry is distinct despite high similarity.
*   **Confidence Score:** 8/10. The logic is deterministic, but the embedding quality depends on the model size.

---

### Self-Correction
**Weakness:** I am assuming the environment can handle the overhead of an embedding model.
**Refinement:** I will verify the memory footprint of the model during the first run. If it exceeds 200MB, I will fallback to a simpler Jaccard-similarity based keyword deduplication to maintain my "minimal footprint" constraint.