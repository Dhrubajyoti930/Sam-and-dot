## Scratchpad

### Option 1: Semantic Cache "Near-Miss" Analysis Dashboard
*   **Concept:** Implement a background task that aggregates queries falling in the 0.15–0.25 cosine distance range, visualizing them as "latent intent" clusters.
*   **Critique:** High value for identifying gaps in the knowledge base. However, it requires adding a clustering dependency (e.g., `scikit-learn`) or a custom centroid-tracking logic, which increases the footprint of `bag/`.
*   **Trade-off:** High insight, but adds complexity to the `bag/` dependency tree.

### Option 2: Embedding Model Versioning & Cache Migration
*   **Concept:** Introduce a `model_version` tag to the semantic cache schema. When the embedding model changes, the system automatically triggers a background re-indexing or invalidation of the cache.
*   **Critique:** Directly addresses the "ghost data" weakness identified in the self-correction. It ensures long-term reliability of the cache.
*   **Trade-off:** Requires a schema migration for existing cache files, but significantly improves the robustness of the system.

**Decision:** Option 2 is more aligned with the "senior engineer" persona. It prioritizes system integrity and prevents technical debt (stale cache) over adding new features.

---

## Idea: Semantic Cache Versioning & Migration Logic

Implement a `model_version` field in the semantic cache metadata and a migration gate in `bag/semantic_cache.py` that invalidates or re-indexes the cache when the embedding model version changes.

## Why
Currently, if the embedding model is updated, the semantic cache becomes a source of "semantic drift," where distance scores are no longer comparable to the new vector space. This leads to silent failures (hallucinations or incorrect hits). Versioning ensures that cache hits are always valid relative to the current embedding model.

## Implementation Steps
1.  **Schema Update:** Modify `bag/semantic_cache.py` to include `model_version` in the cache entry metadata.
2.  **Version Gate:** Add a `get_current_model_version()` function that returns a hash of the current embedding model configuration.
3.  **Migration Logic:** Update `check_cache()` to compare the stored `model_version` with the current version. If they mismatch, trigger `invalidate_cache()` and log the event.
4.  **Logging:** Ensure the `model_version` is included in the structured logs for observability.

## Risk
**Failure Mode:** A mismatch in versioning could trigger a full cache wipe, causing a temporary spike in latency as the cache repopulates.
**Mitigation:** Implement a "soft-invalidation" where the old cache is moved to a `cache_archive/` folder instead of being deleted, allowing for manual recovery if the new model performs poorly.

**Confidence Score:** 9/10