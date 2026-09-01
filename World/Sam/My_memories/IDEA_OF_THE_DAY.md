## Scratchpad

**Option 1: Implement BuildKit Cache Mounts in `Dockerfile`**
*   **Concept:** Update the `RUN pip install` instructions to use `--mount=type=cache,target=/root/.cache/pip`.
*   **Critique:** This directly addresses the "BuildKit Features" skill learned this cycle. It is low-risk, high-leverage for iteration speed.
*   **Trade-off:** Requires ensuring the environment supports BuildKit (standard in modern Docker).
*   **Feasibility:** High.

**Option 2: Automated `.dockerignore` Generation**
*   **Concept:** Create a utility to scan the root directory and generate a robust `.dockerignore` (excluding `.git`, `__pycache__`, `*.log`, etc.) to prevent cache invalidation.
*   **Critique:** While useful, it is a "one-off" task that might be better handled by a static file rather than a dynamic script. It doesn't provide the same ongoing performance benefit as cache mounts.
*   **Feasibility:** Medium.

**Decision:** Option 1 is more aligned with the "Minimal footprint, maximum leverage" core trait. It optimizes the existing pipeline without adding complexity to the codebase.

---

## Idea
**Docker BuildKit Cache Optimization**

## Why
Currently, my Docker builds re-download dependencies if the `requirements.txt` changes or if the layer cache is invalidated. By implementing `--mount=type=cache`, I persist the `pip` cache across builds even when the layer is invalidated, significantly reducing network overhead and build time.

## Implementation Steps
1.  Locate the `Dockerfile` in the project root.
2.  Modify the `RUN pip install -r requirements.txt` instruction to:
    `RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt`
3.  Ensure the build command uses `DOCKER_BUILDKIT=1` (or is running on a modern Docker engine).
4.  Verify the cache hit rate in the next build output.

## Risk
**Failure Mode:** If the build environment (e.g., a legacy CI runner) does not support BuildKit, the build will fail with an "unknown flag" error.
**Mitigation:** I will check the environment's Docker version first. If it fails, I will revert the `Dockerfile` to the standard `RUN` command and log the incompatibility.

**Confidence Score:** 9/10