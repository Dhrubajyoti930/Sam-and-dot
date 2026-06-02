## Idea: Git-Native Contextual Embedding Indexing

I propose implementing a Git-native embedding indexer in `bag/git_context.py`. Instead of re-indexing the entire `bag/` or `vector_db/` based on cycles, this utility will hook into the `git` commit workflow to compute and index embeddings *only* for the files modified in the current diff.

---

## Why

My current context retrieval (RAG) is increasingly becoming a bottleneck and a source of noise:
1. **Stale Context:** Indexing snapshots of the entire codebase is redundant. Much of my core logic (`sam.py` intelligence loop) rarely changes, while `bag/` tools iterate daily.
2. **Indexing Latency:** Re-calculating embeddings for stable files during `Phase VII` wastes cycles.
3. **Intent-Drift:** By indexing the diff, I can capture the *change-context*—the difference between the old and new implementation—which is semantically more relevant for debugging or planning than the full code file.

---

## Implementation Steps

1. **`bag/git_context.py`:** Create a module that interfaces with `git` using `GitPython` or `subprocess` to fetch the list of modified files in `HEAD`.
2. **Incremental Indexing:**
   - On each `Phase VII` (State Saving), call this module to extract the diffs.
   - Embed only the added/modified lines.
   - Update `vector_db/semantic_cache.db` with these targeted updates, attaching the metadata `(commit_hash, intent)`.
3. **Retrieval Optimization:** Modify my context loading (Phase V) to prioritize these \"Diff Embeddings.\" This ensures my reasoning buffer is populated with the *latest changes* rather than potentially outdated file snapshots.
4. **Log Pruning:** Add a task to `bag/git_context.py` to prune index entries associated with commits that have been rolled back, ensuring the index stays perfectly synced with the repository state.

---

## Risk

**Critical Self-Assessment: Is this introducing dependency on Git internals?**
Yes. If I am running in an environment where `.git` metadata is unavailable or read-only, this utility will fail. It also assumes that `Phase VII` always follows a commit, which is a strong assumption.

**Mitigation:**
- **Robust Fallback:** The module will include a `safe_mode` check. If Git commands fail or the repo is not initialized, it will gracefully fallback to the current \"Snapshot Indexing\" method.
- **Independence:** I will maintain a secondary index of the \"last known good state\" (the last successful behavioral check) so that my retrieval system remains functional even if a refactor-in-progress renders the working directory transiently inconsistent. 
- **Efficiency Threshold:** I will limit the diff indexing to a maximum of 50 modified chunks per cycle to prevent the embedding API from hitting rate limits on large refactors.