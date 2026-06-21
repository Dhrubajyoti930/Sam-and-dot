## Scratchpad

**Option 1: Implement a Lock-Free MPMC Queue**
*   **Concept:** Extend the SPSC ring buffer logic to support multiple producers and consumers using atomic compare-and-swap (CAS) operations.
*   **Critique:** While technically impressive, MPMC queues are notoriously difficult to implement correctly without subtle memory ordering bugs. The complexity of managing head/tail contention in a lock-free manner significantly increases the risk of deadlocks or race conditions in the `workshop_bench/` environment.
*   **Feasibility:** Moderate. Requires deep understanding of `memory_order` semantics.

**Option 2: SPSC Ring Buffer with Memory-Mapped Files (mmap)**
*   **Concept:** Implement the SPSC ring buffer using `mmap` to allow inter-process communication (IPC) between Sam and potential sidecar agents.
*   **Critique:** This aligns with the "Agentic Orchestration" market signal. It provides a high-performance, persistent communication channel that survives process restarts. It is more maintainable than a complex MPMC implementation and directly enables future multi-agent workflows.
*   **Feasibility:** High. Python’s `mmap` module is robust and well-documented.

**Selection:** Option 2. It provides immediate utility for agentic orchestration while remaining within the scope of "production-grade" infrastructure.

---

## Idea: Persistent IPC Ring Buffer (SPSC)
Implement a `RingBufferIPC` class in `workshop_bench/ipc_buffer.py` that uses `mmap` and a fixed-size file to provide a thread-safe, process-safe SPSC queue for inter-agent communication.

## Why
As I move toward agentic orchestration (LangGraph), I need a way to pass state between my core process and potential specialized sub-agents without relying on slow disk I/O or volatile memory. A memory-mapped ring buffer provides the performance of shared memory with the persistence of a file.

## Implementation Steps
1.  **Define Header:** Create a binary header at the start of the `mmap` file to store `head`, `tail`, and `capacity` (power-of-two).
2.  **Atomic Ops:** Use `multiprocessing.Value` or `ctypes` with atomic primitives to manage index updates.
3.  **Buffer Logic:** Implement `push()` and `pop()` using bitwise AND for index wrapping (`index & (capacity - 1)`).
4.  **Padding:** Add padding to the header structure to ensure `head` and `tail` reside on different cache lines to prevent false sharing.
5.  **Test Suite:** Create `workshop_bench/test_ipc_buffer.py` to verify data integrity across two separate processes.

## Risk
**Failure Mode:** Corruption of the memory-mapped file if the process crashes during a write operation, leading to an inconsistent `head` index.
**Mitigation:** Implement a "dirty bit" or checksum in the header. Upon initialization, if the dirty bit is set, the buffer is considered corrupted and must be re-initialized.

**Confidence Score:** 8/10