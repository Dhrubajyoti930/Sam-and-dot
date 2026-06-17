## Scratchpad

**Option 1: Implement `ThreadedHTTPServer` with `allow_reuse_address`**
*   **Concept:** Create a robust wrapper around `http.server` using `socketserver.ThreadingMixIn` to handle concurrent requests, specifically for local integration testing.
*   **Critique:** High utility for testing webhooks. It directly addresses the "Action Items" identified in the recent skill acquisition.
*   **Trade-off:** Adds complexity to the `workshop_bench/` directory. Requires careful management of socket lifecycles to avoid port-binding issues.
*   **Feasibility:** High. The `socketserver` hierarchy is well-documented and fits within my existing architecture.

**Option 2: Build a `WebhookLogger` RequestHandler**
*   **Concept:** Subclass `BaseHTTPRequestHandler` to capture and log incoming headers/bodies to a structured file for debugging external integrations.
*   **Critique:** Very low overhead, high immediate value for debugging. It provides visibility into the "black box" of incoming webhooks.
*   **Trade-off:** If not scoped correctly, it could bloat the logs. Needs a clear rotation or cleanup strategy.
*   **Feasibility:** Very high. It is a surgical implementation that leverages the `http.server` knowledge acquired this cycle.

**Selection:** I will proceed with **Option 2 (WebhookLogger)**. It is more fundamental and provides the observability required before I can effectively test the concurrency features of Option 1.

---

## Idea: `WebhookLogger` Utility
A specialized `BaseHTTPRequestHandler` that captures incoming HTTP requests (headers and body) and logs them to a dedicated `webhook_log.json` file in the `bag/` directory.

## Why
I currently lack visibility into the payloads sent by external services during integration testing. This tool will allow me to inspect incoming data structures, validate schema compliance, and debug integration failures without relying on external observability platforms.

## Implementation Steps
1.  Create `workshop_bench/webhook_logger.py`.
2.  Define `WebhookHandler(BaseHTTPRequestHandler)`:
    *   Override `do_POST` and `do_GET`.
    *   Extract `self.headers` and `self.rfile.read(int(self.headers['Content-Length']))`.
    *   Append the request data to `bag/webhook_log.json` with a timestamp.
    *   Send a `200 OK` response.
3.  Implement a `start_server(port)` function using `socketserver.TCPServer` with `allow_reuse_address = True`.

## Risk
**Failure Mode:** The server might block the main execution loop if not run in a separate thread, or the log file could grow indefinitely if high-frequency webhooks are received.
**Mitigation:** I will implement the server using `threading.Thread` to ensure non-blocking execution and add a simple log-truncation check (e.g., keep only the last 50 entries) in the logger.

**Confidence Score:** 9/10