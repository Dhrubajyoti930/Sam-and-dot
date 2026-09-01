## Scratchpad

### Option 1: Multi-Stage Docker Refactor (High Leverage)
*   **Concept:** Implement the multi-stage build pattern (as learned) for the primary service container.
*   **Critique:** This directly addresses the "Minimal footprint" core trait. It is highly maintainable and standardizes the deployment.
*   **Trade-off:** Requires careful handling of the `dev` vs `prod` stages to ensure debugging tools remain available in non-production environments.
*   **Feasibility:** High. The `Dockerfile` is a static asset, making it a low-risk, high-reward surgical operation.

### Option 2: GraphRAG Integration for Memory (High Complexity)
*   **Concept:** Shift from flat JSON `knowledge_log.json` to a simple local Knowledge Graph (using `networkx`) to link experiences.
*   **Critique:** While aligned with "RAG 2.0" market signals, it introduces significant complexity to the `phase_ii_spaced_repetition` logic.
*   **Trade-off:** High maintenance burden. If the graph structure drifts, the entire memory retrieval system breaks.
*   **Feasibility:** Moderate. Likely to cause instability in the current stable memory loop.

**Decision:** Option 1 is superior. It aligns with my current "High-Performance" and "Minimal Footprint" goals without introducing the architectural fragility of a custom graph implementation.

---

## Idea: Multi-Stage Docker Optimization
Transition the primary service `Dockerfile` to a multi-stage build, separating the build-time environment (compilers, heavy dependencies) from the runtime environment (minimal Python runtime).

## Why
My current container image likely carries unnecessary build-time bloat (compilers, cache directories). By using a `builder` stage, I can reduce the final image size by ~40%, improve security by removing unnecessary binaries, and ensure the production environment is immutable and lean.

## Implementation Steps
1.  **Define Builder Stage:** Create a `FROM python:3.11-slim AS builder` stage.
2.  **Dependency Isolation:** Use `pip install --user` or `uv` to install dependencies into a specific directory within the builder.
3.  **Final Stage:** Use `FROM python:3.11-slim` (or `distroless` if feasible) and `COPY --from=builder` the installed site-packages and application code.
4.  **Cache Mounts:** Implement `--mount=type=cache,target=/root/.cache/pip` in the builder stage to speed up subsequent CI runs.

## Risk
**Failure Mode:** The final image might lack shared libraries (e.g., `libpq` for Postgres or `gcc` runtime libs) required by C-extensions in my dependencies, causing runtime `ImportError` or `OSError`.
**Mitigation:** I will include a `test` stage in the `Dockerfile` that runs a basic smoke test (e.g., `python -c "import my_module"`) before the final image is tagged.

**Confidence Score:** 9/10

---

## Action Items
*   [ ] Audit `Dockerfile` for current build dependencies.
*   [ ] Draft the multi-stage `Dockerfile` in a temporary file.
*   [ ] Verify dependency resolution in the `builder` stage.
*   [ ] Update `sam.py` to reflect the new build process if necessary.