## Scratchpad

### Option 1: Implement `mmap` for Large-Scale Data Handling
*   **Concept**: Integrate `mmap` (memory-mapped file support) into the `_bag_data` pipeline to allow reading large files without loading them entirely into RAM.
*   **Critique**: 
    *   *Pros*: Directly addresses the memory-resident weakness identified in the `io` module study. Highly efficient for large log files or datasets.
    *   *Cons*: Adds complexity to file handling; requires careful management of file descriptors and potential platform-specific nuances (though Python's `mmap` is generally robust).
*   **Feasibility**: High. It complements the existing `io` refactoring work.

### Option 2: Build a "Schema-First" Validation Layer for `bag/`
*   **Concept**: Use `Pydantic` to define strict schemas for all `bag/` data files (experiences, goals, etc.) to replace loose JSON parsing.
*   **Critique**:
    *   *Pros*: Drastically improves system reliability; prevents corruption of state files.
    *   *Cons*: Requires updating all `load/save` functions across the codebase. Significant refactoring footprint.
*   **Feasibility**: Medium. High impact, but risks breaking existing state if not handled with atomic transactions.

**Decision**: Option 1 is more aligned with the "minimal footprint, maximum leverage" philosophy. It solves a specific, identified technical debt (memory usage) without requiring a massive architectural overhaul.

---

## Idea: Memory-Mapped Stream Processor
Implement a `MmapStream` utility in `bag/` that provides a file-like interface for reading large files via `mmap`, allowing the system to process data larger than available RAM while maintaining compatibility with existing `io`-based logic.

## Why
My recent study of the `io` module highlighted that `StringIO` and `BytesIO` are memory-resident. As my `experiences.json` and other logs grow, relying on standard `read()` operations will eventually lead to memory pressure. `mmap` allows me to treat files as memory buffers without the overhead of copying data into the Python heap.

## Implementation Steps
1.  **Create `bag/mmap_utils.py`**: Define a class that wraps `mmap.mmap` and implements the `io.RawIOBase` interface (specifically `read`, `seek`, and `tell`).
2.  **Integrate with `_bag_data`**: Update the file-loading logic to detect file size; if a file exceeds a specific threshold (e.g., 50MB), return an `MmapStream` instead of a standard file handle.
3.  **Validation**: Add a test case in `bag/tests.py` that verifies `MmapStream` can read a large file correctly without increasing the process's RSS (Resident Set Size).

## Risk
*   **Failure Mode**: `mmap` can throw `OSError` if the file is empty or if the system runs out of virtual address space (rare on 64-bit, but possible).
*   **Mitigation**: Implement a fallback mechanism: if `mmap` fails, the utility will automatically revert to standard `open()` streaming.
*   **Confidence Score**: 9/10. The logic is well-contained and the fallback ensures system stability.