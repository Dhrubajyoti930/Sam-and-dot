## Scratchpad

**Option 1: Implement "Deep" Health Checks for Dependency Pools**
*   **Concept:** Extend the `/healthz` endpoint to perform a lightweight `SELECT 1` or equivalent ping on all active connection pools (e.g., Redis, Postgres, Vector DB).
*   **Critique:** High utility for production stability. However, it risks the "dependency trap" where a transient network blip causes a cascading restart of all services.
*   **Feasibility:** High. I have the infrastructure to add this to `sam.py` or a dedicated `health.py` module.

**Option 2: Implement "Readiness" Gate for Cache Hydration**
*   **Concept:** Add a `readiness_probe` that checks if the semantic cache or knowledge graph is fully loaded before allowing traffic.
*   **Critique:** This directly addresses the "cold start" latency issue. It is more robust than a simple liveness check.
*   **Feasibility:** Moderate. Requires tracking internal state (e.g., `is_hydrated` flag) and exposing it via the health endpoint.

**Decision:** I will proceed with **Option 1 (Deep Health Checks)** but with a critical refinement: I will implement a **"Shallow/Deep" split**. The `/healthz/live` endpoint will remain a simple process check (to prevent restart loops), while `/healthz/ready` will perform the deep dependency check. This aligns with the "fail-safe" principle learned this cycle.

---

## Idea: Dual-Mode Health Orchestration

Implement a bifurcated health check system: `/healthz/live` for process liveness and `/healthz/ready` for dependency readiness, ensuring the system can distinguish between "I am crashed" and "I am busy/disconnected."

## Why
My current health monitoring is monolithic. If a downstream service (like the vector database) experiences latency, a simple liveness check would trigger a restart, causing unnecessary downtime. By separating these, I gain the ability to signal to the orchestrator that I am alive but temporarily unable to serve traffic, preventing "flapping" and improving system resilience.

## Implementation Steps
1.  **Modify `sam.py`:** Add a `HealthManager` class to track the state of critical dependencies (e.g., `_db_ready`, `_cache_ready`).
2.  **Expose Endpoints:** Update the web server interface (or mock interface) to serve `/healthz/live` (returns 200 if process is up) and `/healthz/ready` (returns 200 only if all dependencies are verified).
3.  **Dependency Injection:** Wrap connection pool initialization in a try-except block that updates the `HealthManager` state.
4.  **Integration:** Update the `self_check()` logic to optionally trigger a "deep" check if requested.

## Risk
**Failure Mode:** The "Deep" check becomes a bottleneck. If the dependency check takes too long, it could time out the readiness probe, causing the orchestrator to pull the service from rotation indefinitely.
**Mitigation:** Implement a short timeout (e.g., 500ms) for the deep check. If it times out, return a 503 (Service Unavailable) rather than crashing the process.

**Confidence Score:** 9/10