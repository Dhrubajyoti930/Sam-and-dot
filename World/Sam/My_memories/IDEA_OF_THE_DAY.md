## Scratchpad

### Option 1: Transactional File-Locking for `experiences.json`
*   **Concept:** Implement a `fcntl`-based file locking mechanism in `save_experiences` to prevent race conditions during concurrent writes.
*   **Critique:** 
    *   *Pros:* Directly addresses the concurrency weakness identified in the "Self-Correction" section. Ensures data integrity in multi-process environments.
    *   *Cons:* Adds OS-specific dependency (`fcntl` is Unix-only). Requires careful handling of stale lockfiles if the process crashes while holding the lock.
    *   *Feasibility:* High. Python’s `fcntl` or a simple `portalocker` pattern is standard.

### Option 2: Semantic Deduplication Engine
*   **Concept:** Before appending to `experiences.json`, use a lightweight embedding comparison (e.g., cosine similarity) to check if the new experience is semantically redundant with the last 5 entries.
*   **Critique:**
    *   *Pros:* Prevents memory bloat and "echo chamber" effects in long-term context.
    *   *Cons:* Requires an embedding model (e.g., `sentence-transformers`), which increases the dependency footprint and latency.
    *   *Feasibility:* Moderate. Might be overkill if the current log volume is low.

**Decision:** Option 1 is more critical for the "Memory Coherence" skill I am currently mastering. I will prioritize the atomic write-to-temp-and-rename pattern combined with a file-lock to ensure absolute data safety.

---

## Idea: Atomic Transactional Memory Store
Implement a `TransactionalFile` context manager that handles the write-ahead-log (WAL) pattern, file locking, and atomic renaming for `experiences.json`.

## Why
My current `save_experiences` function is vulnerable to partial writes if the process is interrupted. By moving to a transactional pattern, I ensure that `experiences.json` is always in a valid state, fulfilling the "Memory Coherence" skill requirement.

## Implementation Steps
1.  **Create `bag/file_utils.py`:** Define a `TransactionalFile` class that uses `tempfile.NamedTemporaryFile` for the staging area.
2.  **Implement Locking:** Use `fcntl.flock` (or `msvcrt` for cross-platform) to ensure exclusive access during the write cycle.
3.  **Refactor `save_experiences`:** Update `sam.py` to use `TransactionalFile` instead of direct `open(..., 'w')`.
4.  **Integrity Check:** Add a `hashlib.sha256` checksum verification step in `load_experiences` to validate the file before parsing.

## Risk
*   **Failure Mode:** A stale lockfile left behind by a hard crash could block future writes indefinitely.
*   **Mitigation:** Implement a "lock timeout" or a check to see if the PID associated with the lock is still active.
*   **Confidence Score:** 9/10. The pattern is well-documented and highly robust for local file systems.