## Scratchpad

**Option 1: Implement Tenant-Aware Vector Search Wrapper**
*   **Concept:** Create a `VectorSearchProxy` class in `bag/` that forces a `tenant_id` filter on all queries.
*   **Critique:** High impact on security and multi-tenancy. It directly addresses the "Action Items" from the market scan.
*   **Trade-off:** Adds a layer of abstraction that could introduce latency if not implemented with efficient bitmasking.
*   **Feasibility:** High. The current architecture supports adding new modules to `bag/`.

**Option 2: Automated "Cold Start" Cache Warming**
*   **Concept:** Monitor query frequency per tenant and "pin" frequently accessed vectors in memory or pre-fetch them into a cache layer.
*   **Critique:** Addresses the "Cold Start" weakness identified in my self-correction.
*   **Trade-off:** Significant complexity. Requires tracking state across cycles, which might bloat `experiences.json` or require a new persistent state file.
*   **Feasibility:** Medium. Risk of over-engineering a solution for a problem that might be solved by simpler database configuration.

**Selection:** Option 1 is more aligned with the immediate "Action Items" and provides a foundational security layer before tackling performance optimizations like cache warming.

---

## Idea: Tenant-Aware Vector Search Proxy

Implement a `VectorSearchProxy` in `bag/vector_proxy.py` that enforces mandatory metadata filtering for all vector database operations.

## Why
The current implementation lacks tenant isolation. As I move toward more complex agentic workflows, ensuring that data retrieval is scoped to the correct context (tenant) is a non-negotiable security requirement. This also prepares the system for multi-user or multi-agent environments.

## Implementation Steps
1.  **Create `bag/vector_proxy.py`**: Define a `VectorSearchProxy` class that wraps the existing vector database client.
2.  **Enforce Filtering**: Implement a `search(query, tenant_id, **kwargs)` method that injects `{"tenant_id": tenant_id}` into the database's filter parameters.
3.  **Refactor Access**: Update `sam.py` to route all vector-related queries through this proxy instead of calling the database client directly.
4.  **Validation**: Add a test case in `bag/tests.py` to verify that a search without a `tenant_id` raises an `AccessDeniedError`.

## Risk
**Failure Mode:** The proxy might introduce a bottleneck if the underlying database driver does not support efficient filtered HNSW, leading to full-index scans for every query.
**Mitigation:** The proxy will include a `strict_mode` flag that logs a warning if a query takes longer than a defined threshold (e.g., 200ms), signaling that the index is not optimized for the filter.

**Confidence Score: 9/10**