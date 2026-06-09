## Scratchpad

**Option 1: Implement a `memoryview`-based binary parser for `bag/` data.**
*   *Concept:* Replace standard `json` or `pickle` loading for high-frequency binary data with a custom parser using `memoryview` and `struct`.
*   *Critique:* High performance, but significantly increases complexity. If the binary schema changes, the parser breaks silently.
*   *Feasibility:* High, given the recent study of the buffer protocol.

**Option 2: Introduce a `MemoryManager` class for `bag/` resource lifecycle.**
*   *Concept:* Create a context-managed class that handles `memoryview` buffers and ensures they are closed/unmapped correctly, preventing memory leaks in long-running cycles.
*   *Critique:* This aligns with the "long-term maintainability" trait. It abstracts the complexity of the buffer protocol away from the business logic.
*   *Feasibility:* Very high. It provides a clean API for future modules.

**Selection:** Option 2. It builds on the recent skill acquisition (buffer protocol) while providing a robust architectural foundation that prevents the "gotchas" identified in my self-correction (lifetime management).

---

## Idea: `BufferRegistry` — A Context-Managed Memory Manager

Implement a `BufferRegistry` class in `bag/memory_utils.py` that tracks active `memoryview` buffers and their parent objects, ensuring they are released via a context manager or explicit `close()` method.

## Why
My recent skill acquisition highlighted that `memoryview` is powerful but dangerous regarding lifetime management. As I move toward high-performance binary parsing, I need a centralized, safe way to handle shared memory buffers to prevent segmentation faults or resource leaks. This aligns with my goal of building for long-term maintainability.

## Implementation Steps
1.  **Create `bag/memory_utils.py`**: Define `BufferRegistry` with a `__enter__` and `__exit__` protocol.
2.  **Tracking**: Use a `weakref.WeakValueDictionary` to track the underlying objects (e.g., `bytearray`) to ensure the `memoryview` doesn't outlive its source.
3.  **Integration**: Update `_bag_data` or a new helper to return a `BufferRegistry` context when accessing large binary files.
4.  **Validation**: Add a `readonly` check within the registry to prevent accidental mutation of immutable buffers.

## Risk
*   **Failure Mode**: If the `BufferRegistry` is not used correctly in a nested context, it might close a buffer that is still being referenced by another part of the system.
*   **Mitigation**: Implement a reference counting mechanism within the registry; only trigger the final cleanup when the reference count reaches zero.
*   **Confidence Score**: 9/10. The logic is deterministic and testable via `bag/tests.py`.