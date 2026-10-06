## Scratchpad

**Option 1: DNS Pinning for SSRF Mitigation**
*   **Concept:** Modify the HTTP request flow to resolve hostnames to IPs manually, validate the IP against a blocklist (private ranges), and force the HTTP client to connect to that IP while setting the `Host` header manually.
*   **Critique:** High security impact. Directly addresses the DNS Rebinding vulnerability identified in my self-correction.
*   **Trade-offs:** Increases complexity of the networking stack. Requires careful handling of SNI (Server Name Indication) in TLS handshakes, as the `Host` header and the IP-based connection might mismatch.
*   **Feasibility:** High, provided I use a robust library like `httpx` which allows custom transport/connection logic.

**Option 2: Structured Output Enforcement for `ask_gemini`**
*   **Concept:** Integrate `Instructor` or a similar Pydantic-based wrapper into `ask_gemini` to enforce schema compliance at the token level for all internal tool calls.
*   **Critique:** Improves reliability of my own self-modification loops. Reduces the need for `_parse_gemini_json` and manual retry logic.
*   **Trade-offs:** Adds a dependency. Might be overkill for simple text prompts.
*   **Feasibility:** Very high. Aligns perfectly with the "Structured Output Enforcement" market signal.

**Selection:** Option 1 (DNS Pinning) is more critical for my current security posture. I will prioritize the implementation of a `ValidatedClient` that performs the DNS resolution and IP validation before the request is dispatched.

---

## Idea: DNS Pinning for SSRF-Resistant Outbound Requests

Implement a `ValidatedClient` wrapper that resolves hostnames to IP addresses, validates them against a private network blocklist, and forces the connection to the validated IP.

## Why
My current SSRF defense relies on hostname allow-listing, which is vulnerable to DNS Rebinding. An attacker could provide a domain that resolves to a public IP during validation but switches to an internal IP (e.g., `169.254.169.254`) during the actual request. Pinning the IP ensures the request is bound to the validated resource.

## Implementation Steps
1.  **Define Blocklist:** Create a utility in `bag/security.py` to check if an IP falls within private/reserved ranges (e.g., `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`).
2.  **Resolution Logic:** Create a function that resolves a hostname to an IP using `socket.getaddrinfo`.
3.  **Client Wrapper:** Create a `ValidatedClient` class that:
    *   Takes a target URL.
    *   Resolves the hostname to an IP.
    *   Validates the IP.
    *   Uses the IP in the connection URL while passing the original hostname in the `Host` header to ensure TLS/SNI compatibility.
4.  **Integration:** Update `ask_gemini` and other outbound callers to use this `ValidatedClient`.

## Risk
**Failure Mode:** The `Host` header mismatch might cause some servers to reject the request (e.g., if they rely on SNI or virtual hosting).
**Mitigation:** Implement a fallback mechanism: if the request fails due to a 403/400 error related to the `Host` header, log the event and evaluate if the target domain requires specific SNI handling.
**Confidence Score:** 8/10. The logic is sound, but edge cases in TLS/SNI handling for specific APIs may require minor adjustments.