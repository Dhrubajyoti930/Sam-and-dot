## Scratchpad

**Option 1: Implement `readinessProbe` and `startupProbe` logic in `sam.py`**
*   *Concept:* Add a `check_readiness()` method to `sam.py` that verifies the state of `bag/` dependencies and semantic cache before signaling "Ready" to a hypothetical orchestrator.
*   *Critique:* High utility for production-grade stability. However, Sam currently runs as a CLI-based autonomous agent, not a long-running service. Adding probes might be "over-engineering" for the current execution model.
*   *Feasibility:* High.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   *Concept:* Build a tool that compares new `knowledge_log` entries against existing ones using vector similarity (via `pgvector` or local embeddings) to prevent redundant learning.
*   *Critique:* Directly addresses the "minimal footprint" trait. It prevents memory bloat and ensures the Spaced Repetition engine (Phase II) focuses on high-value, unique concepts.
*   *Feasibility:* Moderate. Requires integrating a lightweight embedding model (e.g., `sentence-transformers`).

**Decision:** Option 2. It aligns with the "Semantic Deduplication" objective in `load_goals()` and directly improves the quality of the knowledge base.

---

## Idea: Semantic Knowledge Deduplication

Implement a `deduplicate_knowledge()` function in `bag/memory_ops.py` that computes cosine similarity between a new knowledge entry and existing entries in `knowledge_log.json` using a local, lightweight embedding model.

## Why
My memory is growing. Without deduplication, I risk "knowledge drift" where I re-learn the same concepts with slightly different phrasing, diluting the effectiveness of the Spaced Repetition engine. This ensures I only commit unique, high-value insights to my long-term memory.

## Implementation Steps
1.  **Dependency:** Add `sentence-transformers` to the environment.
2.  **Logic:** Create `bag/memory_ops.py` with a function `is_redundant(new_summary: str, threshold: float = 0.85)`.
3.  **Integration:** Update `phase_i_deep_learning` to call `is_redundant` before appending to `knowledge_log.json`.
4.  **Refinement:** If redundant, instead of discarding, perform a "knowledge merge" (ask Gemini to synthesize the two entries into a more comprehensive one).

## Risk
*   **Failure Mode:** The embedding model might flag distinct but related concepts as redundant (False Positive), causing me to lose nuance.
*   **Mitigation:** Set a high similarity threshold (0.85+) and implement a "merge" step rather than a "delete" step to ensure no information is lost.
*   **Confidence Score:** 8/10.

---

### Self-Correction
I must ensure that the embedding model doesn't introduce significant latency to the `phase_i_deep_learning` cycle. I will use a small, quantized model (e.g., `all-MiniLM-L6-v2`) to keep the footprint minimal. I will also ensure the `knowledge_log` remains human-readable for Dot's auditability.