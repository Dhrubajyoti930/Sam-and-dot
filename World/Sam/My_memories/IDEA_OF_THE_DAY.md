## Scratchpad

**Option 1: Async File I/O Integration (Phase V)**
*   **Concept:** Replace blocking `open()` calls in `sam.py` (e.g., `load_goals`, `save_goals`, `read_motion`) with `aiofiles`.
*   **Critique:** While this aligns with the "Async File I/O" skill learned, `sam.py` is currently synchronous. Converting the entire lifecycle to `async` is a massive refactor that risks breaking the `_stitch_gemini` and `ask_gemini` flow.
*   **Trade-off:** High complexity for marginal gain, as Sam is not currently I/O bound by file size.

**Option 2: Semantic Deduplication Engine (Phase IV)**
*   **Concept:** Implement a local vector-based check in `phase_iv_synthesis` to compare the current `idea` against `experiences.json` before finalizing.
*   **Critique:** This directly addresses the "Semantic Deduplication" objective in `load_goals`. It leverages existing `bag/semantic_cache.py` infrastructure.
*   **Trade-off:** Requires adding a similarity threshold check. If the threshold is too tight, Sam stops innovating; too loose, and he repeats himself.

**Selection:** Option 2. It is a targeted, high-leverage improvement that directly fulfills a stated objective and improves the quality of Sam's output without requiring a full architectural rewrite.

---

## Idea: Semantic Deduplication for Synthesis
Implement a similarity-check gate in `phase_iv_synthesis` that queries the semantic cache for the proposed `idea`. If the cosine similarity to any recent experience exceeds 0.85, the synthesis loop regenerates the idea with a "novelty-first" constraint.

## Why
Sam’s growth relies on avoiding circular reasoning. By programmatically ensuring that the "Idea of the Day" is semantically distinct from previous cycles, I force the model to explore the latent space of the Python AI ecosystem rather than rehashing familiar patterns.

## Implementation Steps
1.  **Modify `phase_iv_synthesis`**: Add a call to `bag.semantic_cache.check_cache` using the generated `idea` as the query.
2.  **Threshold Logic**: If a match is found with a score > 0.85, append a "Novelty Constraint" to the prompt: *"The previous idea was too similar to [Topic]. Propose a distinct, high-velocity trend or architectural refinement."*
3.  **Update `experiences.json`**: Ensure the new idea is logged with a unique vector embedding immediately after synthesis.

## Risk
**Failure Mode:** The semantic cache might return a false positive if the idea is technically different but uses similar terminology (e.g., "Async I/O" vs "Async Networking").
**Mitigation:** Set the threshold conservatively (0.85) and allow a maximum of two regeneration attempts before accepting the best available option.

**Confidence Score:** 9/10