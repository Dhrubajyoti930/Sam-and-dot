## Scratchpad

**Option 1: Implement "Semantic Reranking" for `bag/semantic_cache.py`**
*   **Concept:** Currently, the cache uses simple vector similarity. Adding a cross-encoder reranker (e.g., `bge-reranker-v2-m3`) would significantly improve the relevance of retrieved context.
*   **Critique:** High impact on RAG quality. However, it introduces a heavy dependency (PyTorch/Transformers) into the core loop, which contradicts the "minimal footprint" trait.
*   **Feasibility:** Moderate. Requires careful dependency management to avoid bloat.

**Option 2: Automate "Cold Start" Mitigation in `sam.py`**
*   **Concept:** Integrate `readinessProbes` and `startupProbes` logic into the deployment manifests (as identified in the HPA learning cycle).
*   **Critique:** Directly addresses the "Cold Start" weakness identified in the HPA summary. It is a high-leverage, low-complexity change that improves system reliability without adding heavy dependencies.
*   **Feasibility:** High. This is a configuration-level change that aligns perfectly with the current focus on Kubernetes stability.

**Decision:** Option 2. It directly addresses a self-identified weakness and aligns with the "disciplined curiosity" trait by applying the HPA learning immediately.

---

## Idea: Kubernetes Lifecycle Probe Hardening
Implement `startupProbes` and `readinessProbes` in the deployment manifests to synchronize pod availability with application readiness, preventing HPA from triggering redundant scale-up events during initialization.

## Why
The HPA learning cycle highlighted that HPA is often gated by application boot-time performance. Without explicit probes, Kubernetes assumes a pod is ready as soon as the process starts, leading to traffic being routed to uninitialized services and triggering "flapping" in the autoscaler.

## Implementation Steps
1.  **Define Probes:** Create a `probes.yaml` snippet in `bag/` defining a `startupProbe` (to allow for slow initialization) and a `readinessProbe` (to ensure the API is actually serving).
2.  **Patch Manifests:** Use `apply_patch_operations` to inject these probes into the existing deployment configuration.
3.  **Verify:** Run `self_check()` to ensure the YAML structure is valid and `behaviour_check()` to confirm the deployment remains stable.

## Risk
**Failure Mode:** If the `startupProbe` is too aggressive (e.g., timeout too short), the pod will be killed in a crash-loop, causing a permanent outage.
**Mitigation:** Set the `initialDelaySeconds` and `failureThreshold` conservatively (e.g., 30s delay, 5 retries) to allow for worst-case initialization scenarios.

**Confidence Score:** 9/10