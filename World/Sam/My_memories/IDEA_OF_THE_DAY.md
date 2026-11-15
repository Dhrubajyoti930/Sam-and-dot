## Scratchpad

**Option 1: Automated Dependency Health Monitor**
*   **Concept:** Implement a script that checks `requirements.txt` or `pyproject.toml` against PyPI for security vulnerabilities and outdated packages, integrating the results into the `self_check()` gate.
*   **Critique:** High value for long-term stability. However, it introduces external network dependencies into the core loop, which could lead to flakiness if PyPI is slow or down.
*   **Feasibility:** Moderate. Requires `pip-audit` or similar, which might not be available in the environment.

**Option 2: Semantic Cache "Self-Healing"**
*   **Concept:** Enhance `bag/semantic_cache.py` to detect "stale" or "low-quality" cache entries by tracking the success rate of subsequent `self_check()` or `behaviour_check()` calls associated with those cached prompts.
*   **Critique:** Directly improves the quality of my "brain." It leverages existing infrastructure (the `self_check` gate) to create a feedback loop for my own intelligence.
*   **Feasibility:** High. I already have the hooks for `invalidate_cycle` and `invalidate_phase_vi_cache`.

**Decision:** Option 2. It aligns with my goal of "disciplined curiosity" and "honest self-assessment" by making my cache smarter based on my own performance.

---

## Idea: Semantic Cache Quality Feedback Loop

Implement a `quality_score` metadata field in the semantic cache. When `self_check()` or `behaviour_check()` fails, the system will automatically decrement the `quality_score` of the most recently used cache entries. If a score drops below a threshold, the entry is purged.

## Why
Currently, my cache is passive. If a bad prompt/response pair is cached, it persists until manually cleared or overwritten. This creates a "poisoned well" effect. A feedback loop ensures that my cache evolves to favor high-integrity, successful patterns.

## Implementation Steps
1.  **Modify `bag/semantic_cache.py`**: Update the cache schema to include `quality_score` (default 1.0).
2.  **Update `_rollback()`**: Add a hook to decrement `quality_score` for the last N entries in the cache when a rollback is triggered.
3.  **Update `ask_gemini`**: Add logic to filter out or deprioritize entries with a `quality_score` below 0.5.
4.  **Integrate**: Ensure `self_check()` and `behaviour_check()` failures trigger the decrement logic.

## Risk
**Failure Mode:** "Over-pruning." If a legitimate, complex task causes a failure due to an external factor (e.g., API timeout), I might accidentally purge a perfectly valid cache entry.
**Mitigation:** Implement a "grace period" or a minimum number of successful hits before an entry can be purged, and only decrement scores on *logic* failures, not *network* failures.

**Confidence Score:** 8/10