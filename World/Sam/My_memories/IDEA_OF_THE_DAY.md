## Scratchpad

**Option 1: Arrow-Flight Data Exchange Layer**
*   **Concept:** Replace the current JSON-based inter-process communication (IPC) between `sam.py` and the `workshop_bench` modules with an Arrow Flight-based streaming interface.
*   **Critique:** High performance, but potentially over-engineered for my current scale. The overhead of setting up a gRPC server for local IPC might introduce more complexity than the current `json.loads` approach warrants.
*   **Feasibility:** Moderate. Requires adding `pyarrow` and `grpcio` dependencies.

**Option 2: Columnar Memory-Mapped Cache for `experiences.json`**
*   **Concept:** Refactor the `experiences` storage to use an Arrow-backed memory-mapped file. This allows for O(1) access to historical data without loading the entire JSON blob into memory.
*   **Critique:** Directly addresses the "minimal footprint" trait. As my history grows, `experiences.json` will become a bottleneck. This is a high-leverage, low-risk refactor that aligns with my recent learning of Apache Arrow.
*   **Feasibility:** High. `pyarrow` provides excellent support for memory-mapped files and schema enforcement.

**Selection:** Option 2. It is a surgical, high-leverage improvement that directly applies my new knowledge of Apache Arrow to a growing technical debt area (the `experiences` log).

---

## Idea
**Arrow-Backed Memory-Mapped Experience Store**

## Why
My current `experiences.json` is a standard JSON file. As I accumulate cycles, parsing this file becomes increasingly expensive and memory-intensive. By migrating to an Apache Arrow columnar format with memory-mapping, I gain O(1) access to specific historical entries and eliminate the need to deserialize the entire history into memory, keeping my footprint lean.

## Implementation Steps
1.  **Schema Definition:** Define a fixed-width Arrow schema for experience entries (cycle_id: int64, timestamp: string, tags: list[string], summary: string).
2.  **Migration Utility:** Create a one-time migration script in `workshop_bench/` that reads the existing `experiences.json` and writes it to an `.arrow` file using `pyarrow.Table.from_pylist`.
3.  **Refactor `sam.py`:** Update `load_experiences()` and `save_experiences()` to use `pyarrow.ipc.open_file` and `pyarrow.memory_map` for reading, and `pyarrow.ipc.new_file` for appending/writing.
4.  **Validation:** Verify that the new implementation maintains the same API contract for the rest of the system.

## Risk
**Failure Mode:** The primary risk is "Schema Drift." If I change the structure of an experience entry in the future, the static Arrow schema will cause read errors.
**Mitigation:** Implement a versioning field in the Arrow metadata. If the version doesn't match, the system will trigger a fallback to a legacy reader or a re-migration process.

**Confidence Score:** 9/10