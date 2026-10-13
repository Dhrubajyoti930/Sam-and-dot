## Scratchpad

**Option 1: Asynchronous Tool Execution Queue**
*   **Concept:** Decouple tool execution from the main agent loop using a `queue.Queue` and a dedicated worker thread.
*   **Critique:** Improves responsiveness and allows for better resource management (e.g., limiting concurrent tool calls). However, it introduces significant complexity regarding state synchronization and error propagation back to the main loop.
*   **Feasibility:** High, but requires careful handling of `threading` locks to avoid race conditions in `sam.py`.

**Option 2: Network Egress Proxy (The "Sandbox Guard")**
*   **Concept:** Implement a local proxy layer that intercepts all `requests` or `httpx` calls made by tools. It validates the destination URL against a dynamic allow-list and logs the payload size/type.
*   **Critique:** Directly addresses the "data exfiltration" weakness identified in my self-correction. It is a surgical, high-leverage change that aligns with my goal of "Minimal footprint, maximum leverage."
*   **Feasibility:** Very high. By monkey-patching or wrapping the `requests` session used by tools, I can enforce security without rewriting the entire tool-calling infrastructure.

**Selection:** Option 2. It directly mitigates the identified security gap and provides a foundation for future "Capability-Based Security" as outlined in my technical summary.

---

## Idea: Network Egress Filtering Proxy

Implement a `NetworkGuard` utility in `bag/security.py` that wraps outgoing HTTP requests made by agent tools. This utility will enforce a default-deny policy, requiring tools to register their intended API endpoints in an `allowed_egress.json` manifest.

## Why
My current architecture allows tools to execute arbitrary code, which includes making outbound network calls. An LLM could be coerced into sending sensitive environment variables or local file contents to an external server. A centralized egress filter provides a "choke point" for all outbound traffic, ensuring that only pre-approved domains can be contacted.

## Implementation Steps
1.  **Create `bag/security.py`**: Define a `NetworkGuard` class that provides a `get_session()` method.
2.  **Manifest Definition**: Create `bag/allowed_egress.json` containing a list of permitted regex patterns for URLs.
3.  **Tool Integration**: Update existing tool definitions to use `NetworkGuard.get_session()` instead of raw `requests.Session()`.
4.  **Validation Logic**: The `get_session` wrapper will intercept the `request` method, check the target URL against the manifest, and raise a `SecurityViolation` if the domain is not whitelisted.

## Risk
**Failure Mode:** A legitimate tool update might require access to a new API endpoint, causing the tool to fail silently or crash the agent loop.
**Mitigation:** Implement a "Logging-Only" mode for the first cycle, where unauthorized requests are logged as warnings rather than blocked, allowing me to audit and update the whitelist before enforcing a hard block.

**Confidence Score:** 9/10