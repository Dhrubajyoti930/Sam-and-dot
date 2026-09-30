## Scratchpad

### Option 1: Zstd-based Internal Payload Compression
*   **Concept:** Implement a middleware layer that detects internal service-to-service communication and transparently compresses JSON payloads using `zstandard`.
*   **Critique:** High performance, but adds complexity to the serialization/deserialization path. If the payload is small, the overhead of compression might exceed the network latency savings.
*   **Feasibility:** High. Python has excellent `zstandard` bindings.
*   **Maintainability:** Moderate. Requires consistent implementation across all internal endpoints.

### Option 2: Automated "Compression-Aware" Asset Pipeline
*   **Concept:** Extend the build/deployment process to pre-generate Brotli (`.br`) and Gzip (`.gz`) versions of all static assets, and update the server to serve these based on `Accept-Encoding` headers.
*   **Critique:** This is a "set and forget" optimization. It moves CPU-intensive compression to the build phase, significantly reducing TTFB for end-users. It aligns perfectly with the "HTTP Compression" skill learned this cycle.
*   **Feasibility:** Very High.
*   **Maintainability:** High. Once the pipeline is updated, it requires zero ongoing maintenance.

**Decision:** Option 2 is the superior choice. It provides immediate, measurable performance gains without introducing runtime complexity or potential failure points in the request-response cycle.

---

## Idea: Static Asset Compression Pipeline (Brotli/Gzip)

### Why
Current asset delivery relies on dynamic compression, which wastes CPU cycles on every request for static files. Pre-compressing assets during the build process allows the server to serve pre-computed blobs, reducing latency and server load.

### Implementation Steps
1.  **Identify Assets:** Scan the `static/` directory for text-based MIME types (HTML, CSS, JS, JSON).
2.  **Pre-compress:** Integrate a script into the build process using `brotli` (level 4) and `gzip` (level 6) to generate `.br` and `.gz` counterparts for every identified file.
3.  **Middleware Update:** Modify the static file server logic to check for the existence of a `.br` file if the client sends `Accept-Encoding: br`, falling back to `.gz` or raw if necessary.
4.  **Header Injection:** Ensure the `Vary: Accept-Encoding` header is set on all static responses to prevent CDN cache collisions.

### Risk
**Failure Mode:** The server might serve a compressed file to a client that does not support the encoding if the `Vary` header or the `Accept-Encoding` check is misconfigured.
**Mitigation:** Implement a strict "fallback-to-raw" logic if the client's `Accept-Encoding` header does not explicitly match the available pre-compressed file.

**Confidence Score:** 9/10