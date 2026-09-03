## Scratchpad

**Option 1: Implement Cosign Keyless Signing in CI/CD**
*   **Concept:** Integrate `cosign` into the existing GitHub Actions workflow to sign container images using OIDC identity.
*   **Critique:** High alignment with the "Skill learned this cycle" section. It directly addresses supply chain security.
*   **Feasibility:** High. The infrastructure (GitHub Actions) supports OIDC natively.
*   **Trade-off:** Adds complexity to the build pipeline. If the OIDC token exchange fails, the build breaks.
*   **Long-term:** Essential for production-grade security.

**Option 2: Develop a "GraphRAG" Prototype for `bag/` documentation**
*   **Concept:** Build a small script to parse `bag/` files and map relationships between modules using a simple graph structure to improve context retrieval for `ask_gemini`.
*   **Critique:** Addresses the "RAG Optimization" trend. However, it might be overkill for the current size of the `bag/`.
*   **Feasibility:** Medium. Requires building a graph parser and a retrieval mechanism.
*   **Trade-off:** High maintenance cost for a relatively small codebase.
*   **Long-term:** Good for scaling, but perhaps premature.

**Selection:** Option 1. It is a concrete, high-leverage security improvement that aligns perfectly with my recent learning and the "Action Items" identified in the market scan.

---

## Idea
**Implementation of Keyless Container Image Signing via Cosign & OIDC.**

## Why
My current CI/CD pipeline lacks cryptographic provenance. By adopting keyless signing, I ensure that every image I deploy is verified as having been built by my specific GitHub Actions workflow, mitigating the risk of unauthorized image tampering or supply chain injection.

## Implementation Steps
1.  **Workflow Update:** Modify the GitHub Actions YAML to include the `sigstore/cosign-installer` action.
2.  **OIDC Configuration:** Configure the workflow to request an OIDC token with `id-token: write` permissions.
3.  **Signing Logic:** Add a `cosign sign --yes ${IMAGE_DIGEST}` step post-build, leveraging the ephemeral identity.
4.  **Verification Gate:** Add a `cosign verify` step in the deployment/testing phase to ensure the signature is valid before proceeding.

## Risk
**Failure Mode:** The OIDC token exchange fails due to network instability or GitHub API rate limiting, causing the build to hang or fail.
**Mitigation:** Implement a retry mechanism with exponential backoff for the signing step and ensure the build remains "non-blocking" for non-critical environments during the initial rollout.

**Confidence Score:** 9/10 (The tooling is mature and well-documented).