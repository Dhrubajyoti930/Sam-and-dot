## Scratchpad

**Option 1: Differential Privacy Layer for Analytics**
*   **Concept:** Integrate a library like `diffprivlib` into the internal analytics query engine to inject Laplace noise into aggregate metrics.
*   **Critique:** High complexity. Requires deep understanding of the sensitivity of each query. If the noise budget ($\epsilon$) is too high, data is useless; too low, and it's not private.
*   **Trade-off:** High security, but potentially breaks the "truth" of my internal logs.
*   **Feasibility:** Moderate. Requires significant refactoring of the query engine.

**Option 2: HMAC-based PII Pseudonymization Middleware**
*   **Concept:** Create a decorator or middleware that intercepts data before it hits `bag/` storage, hashing sensitive fields with a rotated HMAC key stored in a secure vault.
*   **Critique:** Directly addresses the "Action Items" from the market scan. It is surgical, maintainable, and improves compliance without destroying data utility.
*   **Trade-off:** Adds latency to write operations, but the security gain is substantial.
*   **Feasibility:** High. Fits well with the existing `patch_ops` and `audit` middleware architecture.

**Decision:** Option 2 is superior. It aligns with my current focus on architectural rigor and directly implements the high-priority action item identified in the market scan.

---

## Idea: HMAC-based PII Pseudonymization Middleware

Implement a `Pseudonymizer` middleware that intercepts data writes to `bag/` and automatically masks PII fields using HMAC-SHA256 with a rotated key.

## Why
My current logging and data storage lack a formal boundary between raw data and pseudonymized data. As I scale, the risk of accidental PII leakage in `bag/` increases. This middleware provides a programmatic "safety net" that ensures compliance by design, moving beyond simple masking to cryptographically sound pseudonymization.

## Implementation Steps
1.  **Key Management:** Create `bag/security_vault.py` to handle HMAC key rotation and retrieval.
2.  **Middleware Integration:** Update `bag/patch_ops.py` to include a `Pseudonymizer` class that checks for a `PII_FIELDS` schema tag before writing to disk.
3.  **Transformation:** Implement a `_pseudonymize(data: dict) -> dict` method that applies HMAC to identified fields.
4.  **Verification:** Add a test case in `bag/tests.py` to verify that PII is correctly transformed and that the original value cannot be recovered without the key.

## Risk
**Failure Mode:** The middleware might inadvertently pseudonymize non-PII fields, breaking downstream logic that relies on specific data formats (e.g., timestamps or IDs).
**Mitigation:** Use a strict "allow-list" approach for fields tagged as PII in the schema registry. If a field is not explicitly tagged, it remains untouched.

**Confidence Score:** 9/10