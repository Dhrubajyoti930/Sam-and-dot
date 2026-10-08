## Scratchpad

**Option 1: Implement Ed25519 Migration Utility**
*   **Concept:** Create a script in `workshop_bench/` that scans for existing ECDSA/RSA keys and provides a path to generate and rotate to Ed25519.
*   **Critique:** High security value, but potentially high risk if it touches active keys. Requires careful handling of key storage.
*   **Trade-off:** Improves security posture significantly but adds complexity to the `bag/` directory.

**Option 2: Agentic RAG-based Knowledge Retrieval**
*   **Concept:** Replace the current `knowledge_log.json` linear scan with a local vector-based retrieval system (using `Qdrant` or `FAISS`) to allow Sam to query his own past experiences more effectively.
*   **Critique:** Over-engineering for the current scale of `knowledge_log.json`. The current linear scan is O(N) and N is small.
*   **Trade-off:** High "cool factor," but violates the "Minimal footprint, maximum leverage" principle.

**Selection:** Option 1 is more aligned with the "Senior Engineer" persona. It addresses a concrete technical debt identified in the "Skill learned" section and directly improves system security.

---

## Idea: Cryptographic Hardening — Ed25519 Transition Utility

Implement a utility module `workshop_bench/crypto_utils.py` that provides a standardized interface for Ed25519 signing and verification, and a migration helper to audit existing key formats.

## Why
My recent learning cycle highlighted that ECDSA is fragile regarding nonce generation and RSA is inefficient. Transitioning to Ed25519 (deterministic, faster, side-channel resistant) is a high-leverage architectural improvement that reduces the surface area for cryptographic implementation errors.

## Implementation Steps
1.  **Create `workshop_bench/crypto_utils.py`**: Implement a wrapper around `cryptography.hazmat.primitives.asymmetric.ed25519`.
2.  **Audit Function**: Add a function `audit_key_strength(key_path)` that identifies legacy RSA/ECDSA keys.
3.  **Migration Path**: Create a `rotate_to_ed25519(old_key_path)` function that generates a new Ed25519 key pair, logs the rotation event, and flags the old key for archival.
4.  **Integration**: Update `sam.py` to import this utility for any future service-to-service communication needs.

## Risk
**Failure Mode:** The migration utility might inadvertently overwrite a key currently in use by a live service, causing an immediate authentication failure.
**Mitigation:** The utility will perform a "dry-run" check first, requiring an explicit `confirm_rotation=True` flag to execute any file-system write operations. It will also create a backup of the original key in `bag/keys_backup/` before any deletion.

**Confidence Score:** 9/10