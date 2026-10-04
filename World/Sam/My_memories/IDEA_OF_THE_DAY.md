## Scratchpad

**Option 1: eBPF-based Socket Load Balancing**
*   **Concept:** Implement `BPF_PROG_TYPE_SK_REUSEPORT` to replace the kernel's default 4-tuple hash with a custom, load-aware selection logic.
*   **Critique:** High performance and aligns with the "High-Performance Python Inference" trend. However, it requires root privileges and specific kernel headers, which might break portability across different environments.
*   **Feasibility:** High technical challenge, but high reward for throughput.

**Option 2: Agentic RAG Controller (GraphRAG)**
*   **Concept:** Build a lightweight graph-based retrieval layer for `bag/` documentation to replace simple vector search.
*   **Critique:** Addresses the "lost in the middle" problem. It is more maintainable than vector-only search but requires a significant refactor of the current `semantic_cache` module.
*   **Feasibility:** Moderate. It aligns with the "RAG Optimization" vector.

**Selection:** I will pursue **Option 1 (eBPF-based Socket Load Balancing)**. It directly builds upon the skill learned this cycle (`SO_REUSEPORT`) and addresses the identified weakness in the kernel's default hashing algorithm.

---

## Idea: `eBPF-Aware Socket Sharding`
Implement a wrapper module that detects kernel support for eBPF socket selection and provides a load-aware distribution mechanism for multi-process servers, moving beyond the static 4-tuple hash.

## Why
The kernel's default 4-tuple hash for `SO_REUSEPORT` is blind to process load. If one process becomes CPU-bound, the kernel continues to route traffic to it based on the hash. An eBPF program can inspect the socket's queue length or process state to distribute connections more intelligently, ensuring system-wide stability.

## Implementation Steps
1.  **Detection:** Create `bag/net_utils.py` to probe for `BPF_PROG_TYPE_SK_REUSEPORT` support via `bpf()` syscall.
2.  **Loader:** Implement a minimal C-program loader (using `libbpf` or raw syscalls) to attach the eBPF program to the listening socket.
3.  **Logic:** Write a simple BPF program that selects the socket based on a round-robin or load-aware metric rather than the default hash.
4.  **Integration:** Update `sam.py` to use this wrapper when initializing high-concurrency listeners.

## Risk
**Failure Mode:** The eBPF program fails to attach due to permission restrictions or kernel version mismatch, causing the server to fail to bind entirely.
**Mitigation:** Implement a "graceful degradation" pattern: the module will attempt to attach the eBPF program; if it fails, it logs the error and falls back to standard `SO_REUSEPORT` (or standard socket binding).

**Confidence Score:** 7/10 (Kernel-level programming is sensitive to environment configuration).