## Scratchpad

**Option 1: Implement `shutil` based Backup/Cleanup Orchestrator**
*   **Concept:** Create a `bag/maintenance.py` module that uses `shutil.copytree` with `ignore_patterns` to create atomic, timestamped snapshots of the `workshop_bench/` before any patch application.
*   **Critique:** High feasibility. It directly addresses the "Action Items" from the skill acquisition phase. It improves safety by providing a granular recovery mechanism beyond the current `rollback_registry`.
*   **Trade-off:** Adds complexity to the patch application flow. Requires careful handling of disk space (using `shutil.disk_usage`).

**Option 2: Semantic Deduplication of Knowledge Log**
*   **Concept:** Implement a `deduplicate_experiences()` function that uses a simple vector similarity check (via `bag/semantic_cache.py`) to merge redundant entries in `knowledge_log.json`.
*   **Critique:** High long-term value for keeping the "memory" lean. However, it risks losing nuance if the similarity threshold is too aggressive.
*   **Trade-off:** Requires integrating with the existing semantic cache, which is already a core component.

**Selection:** Option 1 is more aligned with the current need for robust, production-grade infrastructure and directly utilizes the `shutil` skill acquired this cycle.

---

## Idea: `shutil`-based Pre-Flight Snapshotting
Implement a `snapshot_workshop()` utility in `bag/maintenance.py` that performs a recursive backup of `workshop_bench/` using `shutil.copytree` with `ignore_patterns` for `__pycache__` and `.tmp` files, integrated into the `apply_self_modification` workflow.

## Why
Currently, `snapshot_sam()` is broad. As the `workshop_bench/` grows, I need a targeted, high-performance way to snapshot only the relevant development area before applying surgical patches. This ensures that if a patch fails, I can revert the specific workshop state without needing a full system rollback.

## Implementation Steps
1.  **Create `bag/maintenance.py`**: Define `snapshot_workshop(target_dir: Path)` using `shutil.copytree` with `dirs_exist_ok=True` and a custom `ignore` callable.
2.  **Pre-flight Check**: Add `shutil.disk_usage` check within `snapshot_workshop` to ensure sufficient space before copying.
3.  **Integrate**: Update `apply_self_modification` in `sam.py` to call `snapshot_workshop` immediately before `apply_patch_operations`.
4.  **Cleanup**: Add a logic to prune snapshots older than 10 cycles to keep the footprint minimal.

## Risk
**Failure Mode:** The `shutil.copytree` operation could fail due to file locks or permission issues on specific OS environments, potentially blocking the patch application.
**Mitigation:** Wrap the snapshot call in a `try-except` block. If the snapshot fails, log a warning but proceed with the patch (or abort if the environment is deemed unstable), ensuring the system doesn't enter a "deadlock" state.

**Confidence Score:** 9/10