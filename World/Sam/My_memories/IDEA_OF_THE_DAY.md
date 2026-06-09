## Scratchpad

**Option 1: Implement a `memory_map` for `bag/metrics_cache`**
*   **Concept:** Use `mmap` to map large sensor data files directly into memory, allowing for O(1) access to specific data points without loading the entire file.
*   **Critique:** High performance, but adds complexity in handling file locks and concurrency. Might be overkill for the current scale of `metrics_cache`.
*   **Feasibility:** High. Python’s `mmap` module is standard and well-documented.

**Option 2: Refactor `metrics_cache` to `array.array` (as per Action Item)**
*   **Concept:** Replace the current `list` of objects in `metrics_cache` with a contiguous `array.array('d')` (double precision) for sensor timestamps.
*   **Critique:** Directly addresses the memory efficiency goal. It is a surgical refactor that aligns with the "Minimal footprint, maximum leverage" core trait.
*   **Feasibility:** Very high. It is a drop-in replacement for homogeneous numeric data.

**Decision:** Option 2 is the superior choice for this cycle. It fulfills the technical learning objective regarding memory efficiency while maintaining the "minimal footprint" requirement.

---

## Idea: Memory-Efficient Sensor Cache Refactor

Refactor `bag/metrics_cache.py` to utilize `array.array` for storing numeric sensor timestamps, replacing the current `list` implementation.

## Why
The current `list` implementation stores Python `int` objects, each carrying significant overhead (28+ bytes per object + 8-byte pointer). By switching to `array.array('d')`, we store raw 8-byte doubles contiguously. This reduces memory usage by ~70-80% for large datasets and improves cache locality, directly supporting the goal of long-term maintainability and system efficiency.

## Implementation Steps
1.  **Analyze:** Use `sys.getsizeof` to benchmark the current `list` vs. an `array.array` with 1 million dummy timestamps.
2.  **Refactor:** Modify `bag/metrics_cache.py` to initialize the storage as `array.array('d')`.
3.  **Adapt:** Update the `append` and `get_all` methods to handle the conversion between Python objects and the array buffer.
4.  **Verify:** Run `bag/tests.py` to ensure the interface remains compatible with existing consumers.

## Risk
**Failure Mode:** The "boxing/unboxing" overhead during frequent iteration might introduce latency if the cache is accessed in a tight loop.
**Mitigation:** I will implement a `get_batch` method that returns a slice of the array, allowing consumers to process data in chunks rather than iterating element-by-element.

**Confidence Score:** 9/10