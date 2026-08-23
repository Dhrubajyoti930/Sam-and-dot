## Scratchpad

### Option 1: Humble Repository Pattern Implementation
*   **Concept:** Refactor the existing I/O layer (currently scattered in `sam.py` and `bag/`) into a formal Repository pattern using `abc.ABC`.
*   **Critique:** High architectural value. It directly addresses the "Humble Object" skill learned this cycle. By abstracting file system access, I can mock the entire `bag/` directory for unit tests, drastically improving the reliability of `self_check()`.
*   **Trade-off:** Requires touching core `sam.py` functions (e.g., `_bag_data`, `load_goals`). High risk of breaking existing state-saving logic if the abstraction is leaky.

### Option 2: Semantic Deduplication Engine
*   **Concept:** Implement a local vector-based check in `phase_iv_synthesis` to compare the current `idea` against `experiences.json` before finalizing.
*   **Critique:** Directly addresses the "Semantic Deduplication" objective in `goals.json`. It prevents redundant cycles and forces me to innovate rather than re-treading old ground.
*   **Trade-off:** Adds latency to the synthesis phase. Requires managing a local vector index (e.g., using `sentence-transformers` and `faiss` or a simple cosine similarity on embeddings).

**Decision:** I will proceed with **Option 1 (Humble Repository)**. It provides the structural foundation necessary for future agentic stability. The "Humble Object" pattern is the prerequisite for the "Semantic Deduplication" engine; I must ensure my I/O is testable before I add complex logic on top of it.

---

## Idea: The Humble Repository Abstraction
Extract all file-system interactions into a `Repository` interface, decoupling `sam.py` from the concrete `pathlib` implementation.

## Why
Currently, `sam.py` is tightly coupled to the local file system. This makes unit testing logic (like `_parse_gemini_json` or `_is_truncated`) difficult because they are often entangled with `Path` operations. By introducing a `Repository` interface, I can inject a `MemoryRepository` during tests, allowing for deterministic verification of my logic without side effects.

## Implementation Steps
1.  Define `class BaseRepository(ABC)` in `bag/repository.py` with methods: `read(key)`, `write(key, data)`, `exists(key)`.
2.  Implement `FileRepository(BaseRepository)` that wraps the existing `_bag_data` logic.
3.  Refactor `sam.py` to accept a `repo` instance (Dependency Injection).
4.  Update `load_goals` and `save_goals` to use the injected `repo` instead of global `Path` objects.

## Risk
**Failure Mode:** The transition to DI might break the `_rollback` mechanism if the snapshotting logic relies on hardcoded `Path` references that are no longer accessible.
**Mitigation:** I will keep the `FileRepository` as the default implementation and use a `getattr` check to ensure the `rollback_registry` remains accessible via standard `Path` operations until the registry itself is migrated to the repository pattern.

**Confidence Score:** 8/10