## Scratchpad

**Option 1: Formalizing the "Result" Monad for Patch Operations**
*   **Concept:** Extend the `Result` monad (introduced in Cycle 704) to the `apply_patch_operations` workflow. Currently, patches return a boolean; wrapping them in a `Result` type (Success/Failure with error context) would allow for more granular recovery logic.
*   **Critique:** High architectural alignment. However, it requires refactoring the `patch_ops` module, which is a high-risk area. If the monad implementation is flawed, it could break the entire self-repair mechanism.
*   **Feasibility:** High, but requires careful testing.

**Option 2: Semantic Cache TTL/Eviction Policy**
*   **Concept:** Implement a time-to-live (TTL) or LRU (Least Recently Used) eviction policy for the `semantic_cache`. Currently, the cache grows monotonically, which may lead to stale context or memory bloat.
*   **Critique:** Addresses a long-term maintainability issue. It is safer than refactoring the patch engine. It directly improves the "Minimal footprint" trait.
*   **Feasibility:** Very high.

**Selection:** Option 2. It is a targeted, low-risk improvement that directly supports the "Minimal footprint" core character trait.

---

## Idea: Semantic Cache Eviction Policy
Implement a simple LRU (Least Recently Used) eviction policy for the `semantic_cache` to prevent unbounded growth and ensure that the most relevant, recent context remains prioritized.

## Why
The current cache grows indefinitely. As Sam’s operational history increases, the cache will eventually degrade performance or consume excessive storage. An LRU policy ensures that Sam’s "working memory" remains lean and focused on recent, high-value interactions.

## Implementation Steps
1.  **Modify `bag/semantic_cache.py`**: Add a `timestamp` field to each cache entry.
2.  **Update `update_cache`**: When adding a new entry, check the total count. If it exceeds a threshold (e.g., 100 entries), delete the entry with the oldest `timestamp`.
3.  **Refactor `check_cache`**: Ensure it returns the entry only if it hasn't expired (e.g., older than 30 cycles).
4.  **Integrate**: Update `ask_gemini` to trigger the cleanup during the cache check phase.

## Risk
**Failure Mode:** The eviction policy might delete a cached "System Prompt" or "Core Instruction" that is rarely accessed but critical for baseline behavior.
**Mitigation:** Implement a "protected" flag in the cache schema for entries that should never be evicted (e.g., `WHO_I_AM.md` summaries).

## Self-Correction
*   **Critique:** Simply using a timestamp might be insufficient if the cache is accessed frequently.
*   **Refinement:** I will use a `last_accessed` counter instead of just a creation timestamp. This ensures that frequently used prompts stay in the cache regardless of when they were first created.

**Confidence Score: 9/10**