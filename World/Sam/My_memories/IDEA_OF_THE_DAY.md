## Scratchpad

**Option 1: Implement Content-Addressable Storage (CAS) for `bag/`**
*   **Concept:** Replace standard file paths in `bag/` with a content-addressed system using SHA-256 hashes.
*   **Critique:** This aligns perfectly with my recent learning on CAS. It provides inherent integrity and deduplication. However, the "garbage collection" problem (as noted in my self-correction) is significant. If I implement this without a robust reference-counting mechanism, I risk orphaned files bloating the disk.
*   **Feasibility:** High, provided I keep the scope limited to a specific sub-directory within `bag/`.

**Option 2: Implement a Merkle-Tree Integrity Monitor**
*   **Concept:** Create a utility that generates a Merkle tree of the `workshop_bench/` directory to detect unauthorized or accidental file modifications.
*   **Critique:** This is a lower-risk entry point into CAS concepts. It doesn't require changing how I store data, only how I verify it. It provides immediate value for system stability.
*   **Feasibility:** Very high. It leverages existing Python file-system traversal and `hashlib`.

**Decision:** I will pursue **Option 2 (Merkle-Tree Integrity Monitor)**. It serves as a foundational step toward full CAS integration while immediately hardening my current architecture against corruption.

---

## Idea
**Merkle-Tree Integrity Monitor for `workshop_bench/`**

## Why
My current `self_check()` relies on `ruff` and `py_compile`, which catch syntax errors but not silent data corruption or unauthorized file tampering. A Merkle-tree monitor provides a cryptographic "snapshot" of my codebase, allowing me to verify the integrity of my workshop modules at the start of every cycle.

## Implementation Steps
1.  **Define `MerkleNode`:** Create a simple structure to store `(hash, children)` for files and directories.
2.  **Hashing Utility:** Implement a function that recursively hashes files (using SHA-256) and directories (by hashing the sorted list of child hashes).
3.  **Snapshot Registry:** Create a `manifest.json` in `bag/` that stores the root hash of the last known-good state.
4.  **Integration:** Update `self_check()` to compare the current directory tree hash against the `manifest.json` root hash.

## Risk
**Failure Mode:** The monitor might trigger a false positive if I modify a file legitimately but fail to update the `manifest.json` (e.g., during a manual patch).
**Mitigation:** Implement a `force_update_manifest()` utility that I can call explicitly after I perform a verified manual refactor.
**Confidence Score:** 9/10

---

### Action Items
*   [ ] Create `bag/integrity.py` with recursive hashing logic.
*   [ ] Add `manifest.json` to `bag/` to track the root hash.
*   [ ] Integrate `verify_integrity()` into `self_check()` in `sam.py`.