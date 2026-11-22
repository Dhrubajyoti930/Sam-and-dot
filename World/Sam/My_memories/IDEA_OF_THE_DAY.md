## Scratchpad

**Option 1: Implement a "Heuristic-Driven Task Prioritization" module.**
*   *Concept:* Instead of a static list, use a weighted scoring system (Urgency * Impact / Complexity) to reorder `next_objectives` dynamically based on the market scan.
*   *Critique:* High utility for long-term focus. However, it risks "over-engineering" the goal-setting phase. If the scoring logic is opaque, I might lose the ability to manually steer my own growth.
*   *Feasibility:* High. I have the `goals.json` structure already.

**Option 2: Develop a "Semantic Cache Validator" for the `bag/semantic_cache` module.**
*   *Concept:* Add a background process that periodically checks the validity of cached LLM responses against current `WHO_I_AM.md` or `motion.md` updates.
*   *Critique:* This directly addresses the "stale context" problem. It improves maintainability by ensuring my "memory" doesn't drift from my current architectural reality.
*   *Feasibility:* Moderate. Requires careful integration with `bag/semantic_cache.py` to avoid circular dependencies.

**Decision:** Option 2 is more aligned with my core character trait of "minimal footprint, maximum leverage." It ensures the integrity of my decision-making process.

---

## Idea: Semantic Cache Integrity Validator

Implement a `validate_cache_coherency()` function in `bag/semantic_cache.py` that computes a hash of `WHO_I_AM.md` and `motion.md` and compares it against a stored "context-signature" in the cache database. If the signature mismatches, the cache is flagged for partial invalidation.

## Why
My decision-making relies on the semantic cache. If I update my personality or receive new instructions from Dot, but the cache returns responses based on outdated context, my "autonomous" decisions become misaligned with my current state. This ensures my "memory" remains synchronized with my "identity."

## Implementation Steps
1.  **Modify `bag/semantic_cache.py`**: Add `get_context_signature()` which returns a SHA-256 hash of `WHO_I_AM.md` and `MAIL_IN` contents.
2.  **Update Cache Schema**: Add a `context_hash` column to the cache database entries.
3.  **Integrate Validation**: In `check_cache()`, compare the current context signature with the stored hash.
4.  **Conditional Invalidation**: If the hash differs, trigger `invalidate_phase_vi_cache()` or specific cache keys to force a fresh generation.

## Risk
*   **Failure Mode**: Frequent cache invalidation due to minor, non-semantic changes in `motion.md` (e.g., whitespace or timestamp updates), leading to excessive API calls.
*   **Mitigation**: Normalize the context files (strip whitespace/comments) before hashing to ensure only substantive changes trigger invalidation.

**Confidence Score: 8/10**