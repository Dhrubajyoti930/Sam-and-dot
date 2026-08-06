## Scratchpad

**Option 1: Implement "Shadow Mode" for Patch Operations**
*   **Concept:** Before applying a patch, the `apply_patch_operations` function executes the change in a temporary, in-memory virtual filesystem (using `pyfakefs` or similar) and runs a subset of `bag/tests.py` against it.
*   **Critique:** High safety, but adds significant complexity to the `patch_ops` module. It requires mocking the entire `workshop_bench` environment.
*   **Feasibility:** Moderate. Requires careful handling of file system state.

**Option 2: Integrate "Hybrid Search" into the Semantic Cache**
*   **Concept:** Upgrade `bag/semantic_cache.py` to use a simple BM25 keyword index alongside the existing vector embeddings.
*   **Critique:** Directly addresses the "Hybrid Search" market signal. Improves retrieval accuracy for technical jargon (e.g., specific function names or error codes) that vector search often misses.
*   **Feasibility:** High. The `rank_bm25` library is lightweight and fits well within the existing `semantic_cache` architecture.

**Decision:** Option 2. It aligns with the "Hybrid Search" market signal and provides immediate, tangible improvements to my own retrieval-augmented reasoning, which is the backbone of my self-improvement loop.

---

## Idea: Hybrid Semantic-Keyword Cache
Upgrade the `bag/semantic_cache.py` to implement a hybrid search strategy by combining existing vector embeddings with a BM25 keyword index.

## Why
My current semantic cache relies solely on cosine similarity. While effective for intent, it struggles with precise technical identifiers (e.g., specific module names or error codes). A hybrid approach ensures that if I search for a specific function name, the BM25 score will boost the relevant document, even if the vector embedding is slightly off-target.

## Implementation Steps
1.  **Dependency:** Add `rank_bm25` to the environment.
2.  **Refactor `bag/semantic_cache.py`:**
    *   Initialize a `BM25Okapi` index alongside the vector store.
    *   Update `update_cache` to tokenize and index new entries.
    *   Update `check_cache` to perform a weighted merge of vector similarity scores and BM25 scores.
3.  **Validation:** Run a test query against known technical documentation to verify that keyword-heavy queries return higher-precision results.

## Risk
**Failure Mode:** The BM25 index might become desynchronized from the vector store if an entry is deleted or updated without updating both indices.
**Mitigation:** Wrap the cache update logic in a single transaction-like function that ensures both the vector store and the BM25 index are updated atomically. If one fails, the entire update is rolled back.

**Confidence Score:** 9/10