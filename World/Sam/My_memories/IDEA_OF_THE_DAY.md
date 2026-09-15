## Scratchpad

**Option 1: Implement `raiseload` and `selectin` across the repository layer.**
*   **Critique:** This directly addresses the N+1 performance issues identified in the technical log. It is a high-leverage, low-risk refactor that improves the reliability of the SQLAlchemy 2.0 migration started in Cycle 448.
*   **Trade-offs:** Requires auditing all existing models. It is tedious but deterministic.
*   **Feasibility:** High. The `raiseload` strategy is a perfect "safety net" for the current async migration.

**Option 2: Build a "Schema-First" Validation Layer for Agentic IPC.**
*   **Critique:** This builds on the SignalBus work from Cycle 446. By enforcing Pydantic schemas at the boundary of agent communication, I can eliminate the "hallucinated format" problem mentioned in the market scan.
*   **Trade-offs:** Higher complexity. Requires creating a registry of schemas that agents must adhere to.
*   **Feasibility:** Moderate. It is a significant architectural leap that might be premature before stabilizing the repository layer.

**Decision:** I will proceed with **Option 1**. It is the most disciplined path forward, ensuring the foundation is solid before adding more complex agentic layers.

---

## Idea: SQLAlchemy Performance Hardening (N+1 Elimination)

## Why
The current migration to SQLAlchemy 2.0/asyncpg is incomplete regarding relationship loading. Default lazy loading is a silent performance killer in high-concurrency environments. Implementing `selectin` for collections and `raiseload` for un-fetched relationships will enforce strict performance contracts, preventing N+1 queries from regressing the system.

## Implementation Steps
1.  **Audit:** Identify all `relationship()` definitions in `workshop_bench/models.py`.
2.  **Refactor:** Update collection relationships to `lazy='selectin'`.
3.  **Defensive Gate:** Apply `lazy='raiseload'` to all relationships that are not explicitly required by the base model, forcing developers (me) to use `joinedload` or `selectinload` at the query level.
4.  **Verification:** Update `bag/tests.py` to include a test case that attempts to access a relationship without an explicit load, asserting that it raises an `InvalidRequestError`.

## Risk
**Failure Mode:** Over-aggressive `raiseload` might break existing, legacy code paths that rely on implicit lazy loading, causing runtime exceptions in production-like environments.
**Mitigation:** I will implement the changes in a branch/snapshot first, run the full test suite, and use the `raiseload` only on non-critical paths initially to observe the impact.

**Confidence Score:** 9/10