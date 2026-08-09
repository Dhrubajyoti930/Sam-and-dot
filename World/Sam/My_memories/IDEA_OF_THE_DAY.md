## Scratchpad

**Option 1: UoW Pattern Integration (Infrastructure Layer)**
*   **Concept:** Refactor the repository layer to accept a `UnitOfWork` context, ensuring atomicity across multiple repository operations.
*   **Critique:** High architectural value. It directly addresses the "Action Items" identified in the recent skill acquisition. However, it requires a significant refactor of existing service-layer calls.
*   **Feasibility:** Moderate. Requires careful handling of existing state to avoid breaking current functionality.

**Option 2: Graph-RAG Indexing for `bag/` (Knowledge Layer)**
*   **Concept:** Implement a lightweight entity-relationship extractor to index the `knowledge_log.json` and `experiences.json` into a graph structure.
*   **Critique:** Aligns with the "Graph-RAG" market signal. It would significantly improve the quality of Phase II (Spaced Repetition) by allowing Sam to retrieve related concepts rather than just linear history.
*   **Feasibility:** High. The data is already structured; the challenge is the graph traversal logic.

**Selection:** Option 1 (UoW Pattern). It is more fundamental to Sam's long-term stability and directly addresses the "Action Items" generated in the previous cycle.

---

## Idea: Unit of Work (UoW) Transactional Wrapper

Implement a `UnitOfWork` context manager in `bag/uow.py` that manages database/file-system transactions, ensuring that all repository operations within a block either commit successfully or roll back entirely.

## Why
Currently, repository operations are atomic at the file level, but multi-step business transactions (e.g., updating `goals.json` and `experiences.json` simultaneously) are vulnerable to partial failures. A UoW pattern provides a single point of truth for transaction state, improving data integrity and simplifying service-layer logic.

## Implementation Steps
1.  **Create `bag/uow.py`**: Define a `UnitOfWork` class with `__enter__` and `__exit__` methods.
2.  **Repository Injection**: Update `Repository` classes to accept a `uow` instance in their constructor.
3.  **Service Layer Refactor**: Wrap high-level operations (like `phase_vii_state_saving`) in a `with UnitOfWork() as uow:` block.
4.  **Atomic Commit**: Ensure `uow.commit()` is only called if no exceptions occur within the block.

## Risk
**Failure Mode:** "Leaky Abstractions." If the UoW is not correctly implemented, it might hold file locks longer than necessary, leading to contention or deadlocks during concurrent operations.
**Mitigation:** Use a simple `try...except` block within the `__exit__` method to ensure `rollback()` is called on any exception, and keep the UoW scope as narrow as possible.

**Confidence Score:** 8/10. The pattern is well-understood, but the refactoring of existing repository calls requires precision to avoid breaking the current state-saving flow.