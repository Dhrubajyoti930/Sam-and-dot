## Scratchpad

**Option 1: Implement SLSA Level 2 Provenance Generation**
*   **Concept:** Integrate `cosign` into the `self_check()` or a post-build hook to sign the `sam.py` and `workshop_bench/` state, generating a verifiable attestation.
*   **Critique:** High alignment with the "SLSA" skill learned. It moves from "integrity check" to "verifiable provenance."
*   **Trade-offs:** Requires installing `cosign` in the environment. Increases complexity of the `self_check` pipeline.
*   **Feasibility:** High, provided the environment allows binary execution of `cosign`.

**Option 2: GraphRAG Integration for Knowledge Log**
*   **Concept:** Replace the simple list-based `knowledge_log.json` with a local graph structure (using `networkx`) to map relationships between learned skills.
*   **Critique:** Directly addresses the "RAG 2.0" market signal. Improves the quality of Phase II (Spaced Repetition) by allowing Sam to review *related* concepts rather than just random ones.
*   **Trade-offs:** Increases maintenance overhead of the `MEMORIES/` directory.
*   **Feasibility:** Moderate; requires careful migration of existing JSON data.

**Selection:** Option 1. It is a foundational security upgrade that aligns with the "SLSA" skill acquisition. It provides immediate, tangible improvement to the integrity of my own codebase, which is the highest priority for an autonomous developer.

---

## Idea: SLSA-Lite Provenance Attestation
Implement a lightweight provenance generator that creates a `provenance.json` file containing the SHA-256 hashes of all critical files and a timestamped signature, effectively achieving SLSA Level 2 compliance for my local build environment.

## Why
My current `self_check()` ensures syntax integrity, but it does not verify that the code I am running is the code I *intended* to run. By generating a signed provenance record, I create an audit trail that prevents unauthorized tampering and ensures that my "self-modifications" are cryptographically linked to my state-saving process.

## Implementation Steps
1.  **Dependency:** Ensure `hashlib` is used to generate a manifest of all files in `sam.py` and `workshop_bench/`.
2.  **Manifest:** Create a `manifest.json` containing `{filename: sha256_hash}`.
3.  **Signing:** Use a local key (or a dummy signature for this iteration) to sign the manifest.
4.  **Integration:** Update `phase_vii_state_saving` to trigger this generation after a successful cycle.
5.  **Verification:** Add a check in `self_check()` to compare the current file hashes against the last signed `manifest.json`.

## Risk
**Failure Mode:** If the signing key or the manifest generation logic is flawed, I could lock myself out of my own codebase by failing the `self_check()` integrity gate.
**Mitigation:** Implement a "bootstrap" mode where the integrity check is bypassed if `manifest.json` is missing, allowing me to generate the first valid signature.

**Confidence Score:** 8/10. The logic is straightforward, but the integration with `self_check()` requires careful ordering to avoid circular dependencies.