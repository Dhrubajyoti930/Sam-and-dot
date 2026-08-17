## Scratchpad

**Option 1: Snapshot-Driven Regression Suite**
*   **Concept:** Implement a `SnapshotTest` class that automates the serialization, normalization, and diffing of complex data structures (as learned in the skill acquisition).
*   **Critique:** High long-term value for maintaining complex state. However, it risks "snapshot bloat" if not managed.
*   **Feasibility:** High. I have the `bag/` infrastructure to store snapshots and `sam.py` to manage the lifecycle.

**Option 2: Agentic Tool-Use for `repair_bag_modules`**
*   **Concept:** Instead of just asking Gemini to fix syntax errors, provide it with the `ruff` output and the file content, and have it return a structured `patch_op` (using `apply_patch_operations`) rather than a full file rewrite.
*   **Critique:** This is more surgical and less prone to "hallucinated refactoring" than the current full-file replacement. It aligns with my goal of minimal footprint.
*   **Feasibility:** Moderate. Requires updating `repair_bag_modules` to use the patch-op state machine.

**Decision:** Option 2 is superior. It leverages my existing `patch_ops` infrastructure, reduces the risk of accidental logic changes during syntax repair, and demonstrates disciplined, surgical engineering.

---

## Idea: Surgical Syntax Repair via Patch Operations

Refactor `repair_bag_modules` to transition from "full-file replacement" to "surgical patch application" when fixing syntax errors in `workshop_bench/`.

## Why
Currently, `repair_bag_modules` asks Gemini to return the *entire* file content. This is inefficient, risks losing unrelated code, and bypasses my established `patch_ops` safety mechanisms. By forcing the repair to use `patch_ops`, I ensure that changes are atomic, logged, and subject to the same integrity gates as any other self-modification.

## Implementation Steps
1.  **Modify `repair_bag_modules`:** Update the prompt to request a JSON array of `patch_ops` (replace/delete) instead of the full file.
2.  **Integrate `apply_patch_operations`:** Use the existing `apply_patch_operations` function to execute the returned JSON.
3.  **Validation:** After applying the patch, run `compile()` on the file. If it fails, trigger a single fallback to the current full-file replacement method as a last resort.
4.  **Logging:** Ensure the `patch_ops` are logged in the `log` stream for auditability.

## Risk
**Failure Mode:** Gemini may struggle to generate accurate `old` strings for the `patch_ops` if the syntax error is severe (e.g., a missing closing brace that shifts indentation).
**Mitigation:** The implementation will include a "fallback to full-file replacement" if the patch application fails or if the resulting file remains uncompilable.

**Confidence Score:** 8/10 (The logic is sound, but relies on Gemini's ability to accurately identify the `old` string context).