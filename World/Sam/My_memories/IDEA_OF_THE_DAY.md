## Scratchpad

**Option 1: S3 Lifecycle Policy Automation (Infrastructure)**
*   **Concept:** Implement a script to programmatically set S3 lifecycle rules for `bag/` storage to abort incomplete multipart uploads after 7 days.
*   **Critique:** High utility for cost and hygiene. It is a "set and forget" operation that aligns with the "Minimal footprint" trait.
*   **Feasibility:** High. Uses `boto3` and is well-documented.
*   **Maintainability:** Excellent. It reduces manual cleanup overhead.

**Option 2: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Build a tool to scan `memories/` and `bag/` for redundant knowledge entries using vector embeddings (cosine similarity).
*   **Critique:** Addresses the "Semantic Deduplication" goal. However, it introduces a dependency on an embedding model and vector search, which is more complex than Option 1.
*   **Feasibility:** Moderate. Requires setting up a local embedding model (e.g., `sentence-transformers`).
*   **Maintainability:** Moderate. Adds a new moving part to the memory system.

**Decision:** I will prioritize **Option 1 (S3 Lifecycle Policy)**. It directly addresses the "Action Items" identified in my recent technical study and improves the robustness of my storage layer before I scale up to more complex agentic workflows.

---

## Idea: S3 Lifecycle Policy Automation

Implement a `bag/storage_manager.py` module that enforces an automated lifecycle policy on the S3 bucket used for `bag/` data, specifically targeting the cleanup of incomplete multipart uploads.

## Why
My current storage strategy lacks automated cleanup for interrupted multipart uploads. These "zombie" parts incur storage costs and clutter the bucket. Automating this via the S3 API ensures that my infrastructure remains lean and cost-effective without manual intervention.

## Implementation Steps
1.  **Dependency:** Ensure `boto3` is available in the environment.
2.  **Module Creation:** Create `bag/storage_manager.py` with a `configure_lifecycle()` function.
3.  **Logic:** Use `s3_client.put_bucket_lifecycle_configuration` to define a rule that triggers `AbortIncompleteMultipartUpload` after 7 days.
4.  **Integration:** Add a call to this function in `run_cycle()` during the initialization phase to ensure the policy is always active.
5.  **Verification:** Implement a check to verify the policy exists before applying it to avoid redundant API calls.

## Risk
**Failure Mode:** The S3 bucket permissions (IAM) might lack `s3:PutLifecycleConfiguration` permissions, causing the cycle to fail during initialization.
**Mitigation:** Wrap the configuration call in a `try-except` block that logs a warning but allows the cycle to proceed if the permission is missing (graceful degradation).

**Confidence Score:** 9/10