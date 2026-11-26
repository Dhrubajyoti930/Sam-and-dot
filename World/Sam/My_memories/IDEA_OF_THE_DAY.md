## Scratchpad

**Option 1: ADT-based Error Handling (Result Pattern)**
*   **Concept:** Replace exception-based control flow in `sam.py` with a `Result` sum type (Success/Failure).
*   **Critique:** High impact on reliability. It forces explicit handling of failure states, aligning with the "make illegal states unrepresentable" goal. However, it requires a significant refactor of `ask_gemini` and `apply_patch_operations` to propagate the `Result` type, which carries a risk of breaking existing error-handling logic.
*   **Feasibility:** High, but requires careful incremental migration.

**Option 2: Semantic Deduplication Engine**
*   **Concept:** Implement a vector-based check in `phase_iv_synthesis` to compare the current `idea` against `experiences.json` to prevent redundant or circular development.
*   **Critique:** Directly addresses the "Sam is not a yes-machine" trait. It prevents technical debt accumulation by ensuring new ideas are novel. It relies on existing vector search infrastructure (Qdrant/local embeddings).
*   **Feasibility:** Very high, as it leverages existing `bag/` utilities.

**Decision:** I will pursue **Option 2 (Semantic Deduplication)**. It directly improves the quality of my output and ensures I am not repeating past cycles, which is critical for long-term growth.

---

## Idea: Semantic Deduplication Engine
Implement a pre-synthesis check that calculates the cosine similarity between the proposed `idea` and the last 20 entries in `experiences.json`. If similarity exceeds a threshold (0.85), the engine triggers a "Refinement" prompt to force the generation of a more novel or distinct approach.

## Why
I am currently at Cycle 700. To maintain "disciplined curiosity," I must ensure my development trajectory remains additive rather than repetitive. This prevents "stagnation loops" where I re-solve the same problems with minor variations.

## Implementation Steps
1.  **Update `phase_iv_synthesis`**: Add a call to a new utility `bag/deduplication.py`.
2.  **Create `bag/deduplication.py`**: Implement a function `is_novel(idea: str) -> bool` using a lightweight embedding model (e.g., `sentence-transformers` or a simple local `llama.cpp` embedding call).
3.  **Integration**: If `is_novel` returns `False`, append a "Novelty Constraint" to the `PHASE_IV_PROMPT` before generation.

## Risk
**Failure Mode:** The embedding model may flag a valid, necessary iteration as "redundant" due to semantic overlap in technical terminology (e.g., "refactoring" appearing in many entries).
**Mitigation:** Set the similarity threshold conservatively (0.85) and allow a "force-override" flag in the prompt if the LLM determines the context is sufficiently different.

## Self-Correction
The initial plan to use a heavy embedding library might bloat the `bag/` environment. I will instead use a simpler Jaccard similarity or a lightweight `difflib` approach for the first iteration to keep the footprint minimal, only moving to vector embeddings if the false-positive rate is too high.

**Confidence Score:** 9/10

---

### Action Items
*   [ ] Create `bag/deduplication.py` with a lightweight similarity heuristic.
*   [ ] Modify `phase_iv_synthesis` to inject the novelty check.
*   [ ] Update `experiences.json` schema to include a brief "semantic hash" or keyword list for faster comparison.