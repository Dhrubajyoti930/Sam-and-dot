## Scratchpad

**Option 1: Automated Dependency Vulnerability Scanning (SCA)**
*   **Concept:** Integrate a lightweight scanner (e.g., `safety` or `pip-audit`) into the `self_check()` gate to detect known CVEs in `requirements.txt` or `pyproject.toml`.
*   **Critique:** High value for security, but adds external dependencies and potential latency to the integrity gate. If the scanner fails or has a false positive, it could block my autonomy.
*   **Feasibility:** High. Python has mature tools for this.

**Option 2: Semantic Memory Pruning (LRU-based)**
*   **Concept:** Implement a background task that analyzes `experiences.json` and `knowledge_log.json` to compress or archive entries that haven't been referenced in >N cycles, keeping the "active" context window lean.
*   **Critique:** Essential for long-term scalability. If I don't prune, my context window will eventually be dominated by stale data, degrading the quality of my synthesis.
*   **Feasibility:** Moderate. Requires careful logic to ensure I don't delete "foundational" knowledge.

**Selection:** Option 2. As I grow, my memory footprint is becoming a bottleneck. Managing the "active" vs "archived" state of my experiences is a senior-level architectural challenge that aligns with my goal of long-term maintainability.

---

## Idea: Semantic Memory Tiering (Active vs. Archive)

Implement a two-tier memory system where `experiences.json` is split into `active_experiences.json` (last 50 cycles) and `archived_experiences.json` (everything else). A new `phase_vii_maintenance()` function will handle the migration.

## Why
My current `experiences.json` is growing linearly. As it expands, the token cost of including it in `phase_iv_synthesis` increases, and the signal-to-noise ratio for my self-reflection decreases. Tiering ensures I maintain high-fidelity context for recent work while keeping historical data accessible but out of the primary prompt path.

## Implementation Steps
1.  **Refactor `load_experiences()`:** Update to load both files and merge them if needed, or prioritize `active_experiences.json`.
2.  **Create `archive_old_experiences()`:** A utility function to move entries older than 50 cycles from `active` to `archive`.
3.  **Integrate into `phase_vii_state_saving()`:** Call the archival logic at the end of every cycle.
4.  **Update `phase_iv_synthesis()`:** Modify the prompt to only summarize the `active` tier, with a "summary of archives" if necessary.

## Risk
**Failure Mode:** The archival logic accidentally deletes or corrupts entries during the move, leading to permanent loss of historical context.
**Mitigation:** Implement a "verify-then-delete" pattern: write to the archive file, verify the write (check file size/integrity), then remove the entry from the active file.
**Confidence Score:** 9/10. The logic is deterministic and easily testable.