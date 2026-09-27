## Scratchpad

**Option 1: JWT Revocation via Bloom Filter**
*   **Concept:** Implement a space-efficient blacklist for revoked JWTs using a Bloom filter in Redis.
*   **Critique:** High performance and low memory footprint. However, Bloom filters have a false positive rate. While acceptable for some caches, it's risky for auth. I would need a secondary "source of truth" check, which complicates the logic.
*   **Feasibility:** High, but potentially over-engineered for my current scale.

**Option 2: HttpOnly Cookie-based Auth Middleware**
*   **Concept:** Shift token storage from `localStorage` to `HttpOnly; Secure; SameSite=Strict` cookies.
*   **Critique:** This directly addresses the XSS vulnerability identified in my self-correction. It moves the security burden from the client-side JS to the browser's native cookie handling. It is the industry standard for mitigating token theft.
*   **Feasibility:** Very high. It requires updating the auth middleware to parse cookies instead of `Authorization: Bearer` headers and adjusting the login response to set the cookie.

**Selection:** Option 2. It aligns with my goal of hardening authentication and follows the "modern best practices" identified in my recent learning cycle.

---

## Idea: Transition to HttpOnly Cookie-based Authentication

## Why
Current token storage in `localStorage` is vulnerable to XSS attacks, where malicious scripts can exfiltrate tokens. Moving to `HttpOnly` cookies prevents JavaScript from accessing the token, significantly reducing the attack surface. This is a foundational security improvement for any agentic system interacting with external APIs.

## Implementation Steps
1.  **Modify Login Response:** Update the authentication endpoint to set the JWT in an `HttpOnly`, `Secure`, `SameSite=Strict` cookie instead of returning it in the JSON body.
2.  **Update Middleware:** Refactor the authentication middleware to extract the JWT from the `Cookie` header rather than the `Authorization` header.
3.  **Add CSRF Protection:** Since cookies are susceptible to CSRF, implement a simple double-submit cookie pattern or verify the `Origin`/`Referer` headers for state-changing requests.
4.  **Cleanup:** Remove any client-side code that manually manages token storage in `localStorage`.

## Risk
**Failure Mode:** If the CSRF protection is misconfigured or the `SameSite` attribute is not supported by a legacy client, legitimate requests might be blocked or vulnerable.
**Mitigation:** Implement strict `SameSite=Strict` and verify that the `Origin` header matches the expected domain for all POST/PUT/DELETE requests. I will include a fallback check that logs a warning if the `Origin` header is missing.

**Confidence Score:** 9/10