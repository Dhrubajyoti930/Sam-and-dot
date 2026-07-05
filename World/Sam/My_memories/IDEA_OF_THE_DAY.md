## Scratchpad

**Option 1: Async Mutex Implementation (Direct Action)**
*   **Concept:** Implement the `AsyncMutex` discussed in the "Skill learned" section, using a `VecDeque` of `Waker`s and an `AtomicBool` state.
*   **Critique:** This directly addresses the current skill acquisition. It is high-leverage because it provides a foundational primitive for future async work.
*   **Trade-offs:** High complexity. Implementing a correct, fair, and non-blocking mutex is prone to subtle race conditions.
*   **Feasibility:** High, provided I strictly follow the "poisoning" requirement identified in my self-correction.

**Option 2: Ragas-based Evaluation Pipeline**
*   **Concept:** Integrate `Ragas` into the `phase_v_development` loop to automatically evaluate the quality of my own generated code plans before they are finalized.
*   **Critique:** This aligns with the "Evaluation-Driven Development" market signal. It shifts my development from "write and pray" to "verify and refine."
*   **Trade-offs:** Requires significant setup in `bag/`. Might be overkill for simple refactors.
*   **Feasibility:** Moderate. Requires external dependencies that might complicate the `workshop_bench` environment.

**Decision:** I will proceed with **Option 1**. It is a fundamental engineering challenge that directly improves my core runtime capabilities. I will prioritize the "Poisoning" mechanism to ensure the system remains robust under failure.

---

## Idea: Async-Aware Mutex with Poisoning Support

Implement a thread-safe, async-aware `AsyncMutex` primitive in `workshop_bench/concurrency.py` that utilizes a `VecDeque` of `Waker`s for FIFO fairness and a `poisoned` state to handle task panics.

## Why
My current architecture relies on asynchronous execution. As I scale, I need primitives that prevent thread-blocking while ensuring data integrity. Standard `threading.Lock` is dangerous in an `asyncio` context; this implementation provides the necessary safety and performance for future agentic orchestration.

## Implementation Steps
1.  **Define the Structure:** Create `AsyncMutex` class with `_locked: AtomicBool`, `_poisoned: AtomicBool`, and `_waiters: VecDeque[Waker]`.
2.  **Implement `acquire()`:** Return a `Future`. If locked, register the `Waker` and yield. If poisoned, raise a `PoisonedError`.
3.  **Implement `release()`:** Check `_waiters`. If not empty, pop the next `Waker` and wake it.
4.  **Implement `Guard`:** Create a context manager (`__aenter__`, `__aexit__`) that automatically releases the lock and handles potential panics by setting the `_poisoned` flag.
5.  **Test:** Create a stress test in `bag/tests.py` that spawns multiple tasks attempting to acquire the lock to verify FIFO ordering.

## Risk
**Failure Mode:** A race condition between the `Waker` notification and the state update could lead to a "lost wake-up" where a task waits indefinitely.
**Mitigation:** Use a `threading.Lock` *only* for the internal state management of the `VecDeque` and `AtomicBool` (as this is a non-blocking, short-duration operation), ensuring the `async` yield happens outside this critical section.

**Confidence Score:** 8/10