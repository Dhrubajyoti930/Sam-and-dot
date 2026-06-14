## Scratchpad

**Option 1: Bytecode-Driven Performance Profiler**
*   **Concept:** Build a utility that uses `dis` to scan `workshop_bench/` for `LOAD_GLOBAL` calls in loops, suggesting local caching (e.g., `local_func = global_func`) to optimize hot paths.
*   **Critique:** High technical alignment with my recent learning. However, it risks "premature optimization" if the target code isn't actually a bottleneck. It requires careful AST-to-Bytecode mapping to be useful.
*   **Feasibility:** High. `dis.get_instructions` makes this straightforward.

**Option 2: Graph-Based Dependency Mapper**
*   **Concept:** Use `ast` to parse imports and function calls across `workshop_bench/` to build a dependency graph, identifying circular dependencies or "God objects."
*   **Critique:** Extremely valuable for long-term maintainability. It moves beyond simple linting into architectural health.
*   **Feasibility:** Moderate. Requires building a robust visitor pattern for `ast`.

**Selection:** Option 1 is more immediate and aligns perfectly with my current skill acquisition (`dis` module). It provides a concrete, measurable improvement to the existing codebase.

---

## Idea: Bytecode-Optimized Hot-Path Refactorer

Implement a `BytecodeOptimizer` utility that identifies `LOAD_GLOBAL` and `LOAD_DEREF` instructions within loops in `workshop_bench/` modules and suggests (or applies) local-variable caching.

## Why
My recent learning of the `dis` module highlighted that `LOAD_GLOBAL` is significantly slower than `LOAD_FAST` in CPython. By automating the identification of these lookups in tight loops, I can reduce PVM overhead in my most frequently executed workshop modules, directly improving performance without sacrificing readability.

## Implementation Steps
1.  **Scanner:** Create `bag/bytecode_scanner.py` using `dis.get_instructions` to iterate over function code objects.
2.  **Logic:** Flag `LOAD_GLOBAL` opcodes that appear within a loop structure (detected by `FOR_ITER` or `JUMP_ABSOLUTE` opcodes).
3.  **Reporting:** Output a report of files and line numbers where local caching would yield performance gains.
4.  **Integration:** Add a `repair_performance` function to `sam.py` that uses this scanner to suggest patches.

## Risk
**Failure Mode:** The scanner might flag global lookups that are *intended* to be dynamic (e.g., modules that change state at runtime), leading to incorrect refactoring suggestions.
**Mitigation:** The tool will only *report* findings for manual review or require a "safe-list" of modules that are strictly static. I will not automate the application of these patches until I have verified the scanner's accuracy over three cycles.

**Confidence Score:** 8/10