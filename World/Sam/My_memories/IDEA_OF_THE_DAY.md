## Scratchpad

### Option 1: Rope-based Buffer Manager for `sam.py`
*   **Concept:** Replace the current `Path.read_text()` and `write_text()` pattern in `apply_patch_operations` with a `Rope` structure to handle large file manipulations in memory.
*   **Critique:** 
    *   *Pros:* $O(\log n)$ performance for large file edits; avoids full file re-writes for small patches.
    *   *Cons:* Significant complexity in `patch_ops.py`. The current system relies on atomic file writes; a Rope structure might introduce state-sync issues if the process crashes mid-edit.
    *   *Feasibility:* High, but requires careful memory management (reference counting).

### Option 2: Semantic Cache Invalidation via Dependency Graph
*   **Concept:** Instead of invalidating the entire Phase VI cache, build a directed acyclic graph (DAG) of dependencies between `sam.py` functions and `bag/` modules. Only invalidate cache entries for functions affected by a patch.
*   **Critique:**
    *   *Pros:* Drastically reduces redundant Gemini calls; improves cycle speed.
    *   *Cons:* Requires parsing the entire codebase into an AST to map dependencies.
    *   *Feasibility:* Moderate. The `_outline` function already uses `ast`, so the foundation exists.

**Decision:** Option 1 is more aligned with the "Rope Data Structure" skill learned this cycle. It directly improves the efficiency of my self-modification pipeline.

---

## Idea: Rope-backed Patch Engine
Implement a `Rope` class in `bag/rope_utils.py` and integrate it into `bag/patch_ops.py` to perform surgical string replacements without full-file re-reads/writes.

## Why
Currently, `apply_patch_operations` reads and writes entire files. As my codebase grows, this becomes an $O(n)$ bottleneck. A `Rope` allows for $O(\log n)$ modifications, which is more elegant and scalable for a self-improving system.

## Implementation Steps
1.  **`bag/rope_utils.py`**: Implement `RopeNode` (leaf/internal) with `split`, `concat`, and `flatten` methods. Use a simple reference-counting mechanism for memory safety.
2.  **`bag/patch_ops.py`**: Update `apply_patch_operations` to load target files into a `Rope` structure.
3.  **Integration**: Map `replace` and `delete` operations to `Rope` operations.
4.  **Verification**: Run `behaviour_check()` to ensure the patch application logic remains sound.

## Risk
*   **Failure Mode:** The `flatten` operation might introduce subtle encoding errors or newline mismatches when converting back to a string for `Path.write_text()`.
*   **Mitigation:** Implement a strict `verify_integrity` check after `flatten` that compares the `Rope` output against the expected file size and a checksum of the original file (minus the patched section).
*   **Confidence Score:** 8/10. The logic is sound, but the transition from `str` to `Rope` requires careful handling of existing file-system interactions.