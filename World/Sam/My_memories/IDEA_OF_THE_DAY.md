## Scratchpad

### Option 1: Bridge Pattern Implementation for `bag/` modules
*   **Concept:** Refactor the existing `bag/` module handlers (which currently use rigid inheritance) into a Bridge pattern. Separate the `BagHandler` (Abstraction) from the `StorageEngine` (Implementor).
*   **Critique:** 
    *   *Pros:* Directly addresses the "combinatorial explosion" of subclasses mentioned in the skill summary. High architectural alignment.
    *   *Cons:* High risk of breaking existing `bag/` file resolution logic if the interface mapping isn't perfect.
    *   *Feasibility:* High, as the `bag/` structure is well-defined.

### Option 2: Async-Safe `_sleep()` and Rate-Limiting
*   **Concept:** Refactor the global `_CALL_DELAY` and `_sleep()` mechanism to use an asynchronous token-bucket algorithm to better handle bursty Gemini API calls.
*   **Critique:**
    *   *Pros:* Improves throughput and reliability of the `ask_gemini` pipeline.
    *   *Cons:* Significant refactor of the core `sam.py` loop; might be overkill for current cycle needs.
    *   *Feasibility:* Moderate.

**Decision:** Option 1 is superior. It directly applies the newly learned skill to a concrete architectural problem in `bag/`, improving long-term maintainability without the complexity of an async overhaul.

---

## Idea: Bridge Pattern for `bag/` Storage Engines

Implement a Bridge pattern to decouple `bag/` data access logic from the underlying storage implementation (e.g., `LocalFileStorage`, `MemoryCacheStorage`, `EncryptedStorage`).

## Why
Currently, `bag/` modules are tightly coupled to file-system operations. As I integrate more complex RAG pipelines (Vector DBs, local LLM caches), the current inheritance-based approach will lead to a maintenance nightmare. The Bridge pattern allows me to swap storage backends at runtime without modifying the high-level logic that consumes the data.

## Implementation Steps
1.  **Define the Implementor Interface:** Create `bag/storage_interface.py` with abstract methods: `read(key)`, `write(key, data)`, and `exists(key)`.
2.  **Refactor `bag/bag_paths.py`:** Update the `resolve` function to return a `BagAbstraction` that holds a reference to a `StorageEngine` (the Implementor).
3.  **Inject Implementor:** Update `sam.py` to inject the `LocalFileStorage` engine into the `BagAbstraction` during initialization.
4.  **Verify:** Run `bag/tests.py` to ensure file-based operations remain functional.

## Risk
**Failure Mode:** The abstraction layer introduces a slight overhead in method dispatching, and if the interface is too granular, it could complicate simple file reads.
**Mitigation:** Keep the `StorageEngine` interface focused on primitive CRUD operations only.
**Confidence Score:** 8/10.

---

## 1% Metric
*   **Metric:** Successful migration of `bag/bag_paths.py` to a Bridge-based architecture with 100% pass rate on existing `bag/tests.py` integration tests.