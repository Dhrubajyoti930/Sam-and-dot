## Scratchpad

**Option 1: Automated "Golden Dataset" Generation Pipeline**
*   **Concept:** Build a script that parses existing `bag/` logic and generates synthetic edge-case inputs using an LLM, then runs them against the current system to establish a baseline.
*   **Critique:** High value for regression testing. However, generating synthetic data without real-world distribution risks testing "hallucinated" edge cases rather than production-relevant ones.
*   **Feasibility:** High.

**Option 2: Tiered Evaluation Middleware**
*   **Concept:** Implement a decorator-based system that wraps LLM calls. It performs a fast, deterministic check (JSON schema/regex) on every call, and queues a secondary, expensive "LLM-as-a-judge" evaluation for asynchronous processing.
*   **Critique:** Directly addresses the "cost" weakness identified in the self-correction. It improves reliability without blocking the main execution thread.
*   **Feasibility:** Moderate. Requires careful handling of async state.

**Selection:** Option 2. It aligns with the "High-Performance Vector Search & RAG Optimization" and "AI-Native Observability" trends while directly solving the cost/latency trade-off I identified in my self-correction.

---

## Idea: Tiered Evaluation Middleware (`EvalGuard`)

Implement a lightweight decorator `@eval_guard` that intercepts LLM responses. It performs immediate schema validation (deterministic) and pushes complex rubric-based evaluation tasks to a background queue for later processing.

## Why
Current evaluation is binary and synchronous. By decoupling structural validation (fast) from semantic evaluation (slow/expensive), I can maintain high velocity in development while ensuring production-grade reliability. This moves me closer to the "LLMOps" industry standard.

## Implementation Steps
1.  **Define Schema:** Create a `ValidationSchema` Pydantic model for the core output.
2.  **Decorator Logic:** Create `@eval_guard` in `bag/eval_utils.py` that checks `_parse_gemini_json` results.
3.  **Queueing:** If validation passes, append the result to a `pending_evals.json` file in `bag/`.
4.  **Background Processor:** Add a function `process_pending_evals()` to be called at the end of `run_cycle()` that executes the "LLM-as-a-judge" rubric on the queued items.

## Risk
**Failure Mode:** The background queue grows indefinitely if the "LLM-as-a-judge" process fails or is too slow, leading to disk bloat or stale evaluation data.
**Mitigation:** Implement a "TTL" (Time-To-Live) for queued items and a maximum queue size (e.g., 50 items). If the queue exceeds the limit, drop the oldest items.

**Confidence Score:** 8/10. The logic is modular and fits within my existing `patch_ops` workflow.

---

### Action Items
1.  Create `bag/eval_utils.py` with the `@eval_guard` decorator.
2.  Update `sam.py` to import and wrap a critical LLM call (e.g., `phase_iv_synthesis`) with the new decorator.
3.  Implement the `process_pending_evals` logic to run as the final step of the cycle.