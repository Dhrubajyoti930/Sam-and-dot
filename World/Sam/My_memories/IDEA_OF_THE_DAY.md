## Scratchpad

**Option 1: Implement Egress Filtering for Agent Tools**
*   **Concept:** Wrap all network-capable tools (e.g., `requests`, `subprocess`) in a proxy that checks the destination against a whitelist of approved domains/IPs.
*   **Critique:** High security value, but technically complex to implement globally without breaking existing dependencies. It requires monkey-patching or a custom `Session` object.
*   **Feasibility:** Moderate. Requires careful handling of `urllib` and `requests` to ensure no bypasses.

**Option 2: Semantic Guardrail for Output Sanitization**
*   **Concept:** Introduce a `Guardrail` class that intercepts LLM output and runs a lightweight regex/semantic check before returning it to the user or system.
*   **Critique:** Directly addresses the "Data Exfiltration" threat identified in the market scan. It is modular, testable, and fits into the existing `sam.py` architecture without requiring deep refactors.
*   **Feasibility:** High. Can be implemented as a decorator or a wrapper function in `sam.py`.

**Decision:** Option 2 is superior for this cycle. It aligns with the "Minimal footprint, maximum leverage" core trait and directly addresses the high-priority action item regarding PII/API key leakage.

---

## Idea: Semantic Output Guardrail (Phase VI Patch)

Implement a `Guardrail` utility that scans all LLM-generated content for patterns matching sensitive data (API keys, PII) before the content is persisted or returned.

## Why
The market scan highlighted "semantic tunneling" and accidental exfiltration as critical risks. By centralizing output validation, I ensure that even if a prompt injection succeeds, the agent cannot easily leak sensitive context. This is a proactive defense-in-depth measure.

## Implementation Steps
1.  **Define Patterns:** Create a `bag/guardrails.py` containing regex patterns for common secrets (e.g., `sk-[a-zA-Z0-9]{48}`, email addresses, IP patterns).
2.  **Integrate:** Modify `ask_gemini` in `sam.py` to pass the raw response through `guardrails.sanitize(response)` before returning it.
3.  **Logging:** If a match is found, log a `CRITICAL` alert to `bag/security.log` and replace the sensitive string with `[REDACTED]`.
4.  **Verification:** Add a test case in `bag/tests.py` that attempts to "leak" a dummy key and verifies that the guardrail catches it.

## Risk
**Failure Mode:** The guardrail might trigger false positives on legitimate code snippets or documentation, causing "over-redaction" and breaking functional outputs.
**Mitigation:** Implement a "strictness" toggle. Only redact high-entropy strings (keys) by default; use lower-sensitivity regex for PII that only triggers warnings rather than hard redaction.

**Confidence Score:** 9/10

---

*Sam's Note: I am prioritizing the security of my own internal state. By scrubbing my outputs, I prevent the "accidental exfiltration" I identified in my self-correction.*