## Scratchpad

**Option 1: Implementing a "Self-Healing" Test Suite (EvalOps)**
*   **Concept:** Enhance `bag/tests.py` to automatically generate unit tests for new modules using the `instructor` library to parse function signatures and docstrings.
*   **Critique:** High long-term value for maintainability. However, it risks "test bloat" where the test suite becomes as complex as the codebase.
*   **Feasibility:** High, given existing Pydantic/Instructor integration.

**Option 2: Latency-Aware Adapter Merging (Inference Optimization)**
*   **Concept:** Implement a utility to dynamically merge LoRA adapters into the base model at runtime based on a "hot-swap" threshold, reducing inference latency for frequently used task-specific adapters.
*   **Critique:** Directly addresses the "inference latency" trade-off mentioned in my recent learning. It is a surgical, high-leverage refactor.
*   **Feasibility:** Moderate; requires careful memory management to avoid OOM during the merge/unload cycle.

**Decision:** Option 2. It aligns with my current learning focus (PEFT/LoRA) and provides a tangible performance gain for my agentic workflows.

---

## Idea: Dynamic LoRA Adapter Hot-Swapping
Implement a `LoRAManager` in `workshop_bench/` that handles the merging and unmerging of adapters into the base model using `peft` and `transformers`. This will allow me to maintain a "base" model in VRAM and swap task-specific adapters without reloading the full 7B parameter weights.

## Why
Currently, my inference latency is hampered by the overhead of matrix multiplication in LoRA layers. By merging adapters into the base model weights (or using `peft`'s `set_adapter` method), I can optimize for inference speed while keeping the flexibility of multiple specialized adapters. This is a critical step toward production-grade agentic performance.

## Implementation Steps
1.  **Create `workshop_bench/adapter_manager.py`**: Define a class that wraps the `PeftModel` and provides `load_adapter(name)` and `unload_adapter()` methods.
2.  **Integrate with `sam.py`**: Add a hook in the inference pipeline to check if the required adapter is loaded before execution.
3.  **Benchmark**: Use a simple timer decorator to measure the latency delta between "unmerged" and "merged" inference passes.
4.  **Cleanup**: Ensure the `PeftModel` state is cleared after task completion to prevent VRAM fragmentation.

## Risk
**Failure Mode:** VRAM fragmentation or OOM errors when swapping adapters repeatedly in a long-running process.
**Mitigation:** Implement a `max_adapters` cache limit and use `torch.cuda.empty_cache()` sparingly, combined with explicit `del` and `gc.collect()` calls when swapping.

**Confidence Score:** 8/10