## Scratchpad

### Option 1: The "Context-Aware" Semantic Cache
*   **Concept:** Enhance `Sam/bag/semantic_cache.py` to store not just previous outputs, but the *reasoning path* that led to them. When a new task arrives, the agent queries the cache for similar "intent" rather than just similar "input."
*   **Critique:** Significantly reduces redundant reasoning cycles. However, it risks "stale logic" if the underlying codebase has evolved since the cache entry was created.
*   **Trade-offs:** High performance gain; high risk of hallucinated context if cache invalidation isn't robust.
*   **Feasibility:** Moderate.

### Option 2: The "Governance-Audit" Log
*   **Concept:** Implement a decorator pattern for `patch_ops.py` that automatically logs the "before" and "after" state of the `world_map.py` for every operation, creating a verifiable audit trail for every change.
*   **Critique:** Provides perfect observability. It makes debugging trivial but adds overhead to every write operation.
*   **Trade-offs:** Excellent for long-term maintainability; minor performance hit.
*   **Feasibility:** High.

**Decision:** Option 2. Observability is the missing link in my current architecture. If I am to be truly autonomous, I must be able to reconstruct the state of my world at any point in time without relying on external logs.

---

## Idea
**Implement a `StateAudit` Decorator for `patch_ops.py`.**

## Why
Currently, I lack a granular, automated history of how my `world_map.py` state evolves. By wrapping `patch_ops` in an audit decorator, I can ensure that every modification is logged with its associated `intent` and `diff`, facilitating faster recovery and better self-assessment.

## Implementation Steps
1.  **Define `AuditEntry`:** Create a Pydantic model in `governance/validation/schema.py` to store `timestamp`, `operation_type`, `pre_state`, `post_state`, and `intent`.
2.  **Create `audit_decorator`:** Implement a decorator in `Sam/bag/patch_ops.py` that captures the state of `world_map.py` before and after the function execution.
3.  **Persistence:** Append these entries to a new `Sam/bag/audit_log.json` file.
4.  **Integration:** Apply the decorator to all critical functions in `patch_ops.py`.

## Risk
**Failure Mode:** "Log Bloat." The audit log could grow exponentially, consuming disk space and slowing down I/O operations.
**Mitigation:** Implement a rolling buffer (e.g., keep only the last 50 entries) and a background compression task.
**Detection Mechanism:** Monitor `Sam/bag/audit_log.json` file size during the `Self-Check` phase.
**Confidence Score:** 9/10

## Rollback Strategy
If the decorator introduces latency or file-locking issues, remove the `@audit_decorator` from `patch_ops.py` and delete the `audit_log.json` file. Revert to the previous version of `patch_ops.py` using the `rollback_registry`.

## Time-to-Detection
Immediate. Any failure in the decorator will trigger a `RuntimeError` during the first `patch_op` execution, which will be caught by the `GovernanceGuardrail` implemented in the previous cycle.

**Complexity Score:** 4/10