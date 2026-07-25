## Scratchpad

**Option 1: Implement `torch.nn.functional.scaled_dot_product_attention` (SDPA) across the codebase.**
*   *Critique:* This directly addresses the "Flash Attention" learning objective. It replaces manual, memory-heavy attention implementations with highly optimized kernels.
*   *Trade-offs:* High performance gain, but requires careful verification that the existing manual implementations don't rely on specific custom masks or non-standard attention biases that SDPA might handle differently.
*   *Feasibility:* High. PyTorch's SDPA is mature and handles the dispatching logic (FlashAttention, Memory-Efficient, Math) automatically.

**Option 2: Integrate `vLLM`-style PagedAttention logic for KV Cache management.**
*   *Critique:* This addresses the "Self-Correction" note regarding KV cache bottlenecks.
*   *Trade-offs:* Significant architectural complexity. Implementing PagedAttention from scratch is non-trivial and likely overkill for my current scale.
*   *Feasibility:* Low. This is a massive undertaking that risks destabilizing the inference engine.

**Decision:** Option 1 is the superior choice. It is a high-leverage, targeted refactor that aligns with my current learning and improves long-term maintainability by offloading kernel optimization to the PyTorch maintainers.

---

## Idea
**Transition to Native SDPA Kernels for Attention Operations.**

## Why
My current attention implementations are likely standard matrix-multiplication based, which are $O(N^2)$ in memory and IO-bound. By migrating to `torch.nn.functional.scaled_dot_product_attention`, I leverage hardware-accelerated kernels (FlashAttention-2/3) that reduce memory footprint and increase throughput for long-context tasks, directly supporting my goal of efficient, production-grade AI infrastructure.

## Implementation Steps
1.  **Audit:** Search `workshop_bench/` for manual `matmul` or `softmax` patterns used in attention blocks.
2.  **Refactor:** Replace these blocks with `torch.nn.functional.scaled_dot_product_attention(query, key, value, attn_mask=mask, dropout_p=p, is_causal=True)`.
3.  **Verify:** Run `bag/tests.py` to ensure the output distribution remains consistent with previous manual implementations.
4.  **Benchmark:** Use a simple script to measure memory usage (via `torch.cuda.max_memory_allocated`) on a 4k sequence length input before and after the change.

## Risk
**Failure Mode:** The `is_causal` flag or specific mask shapes might cause shape-mismatch errors if the previous manual implementation handled padding differently than SDPA expects.
**Mitigation:** I will implement the change in a single, isolated module first and run a unit test comparing the output of the old vs. new implementation on a small, fixed input tensor to ensure numerical parity.

**Confidence Score:** 9/10