## Scratchpad

**Option 1: Token-Aware Context Pruning (Action Item 1 & 2)**
*   **Concept:** Implement a `tiktoken`-based utility to monitor context usage and a pruning function to summarize historical logs when exceeding 70% capacity.
*   **Critique:** This is a high-leverage, foundational improvement. It directly addresses the "lost in the middle" phenomenon and ensures long-term stability as my interaction history grows.
*   **Trade-off:** Requires careful handling of the `knowledge_log.json` and `experiences.json` to ensure summaries remain high-fidelity.
*   **Feasibility:** High. `tiktoken` is standard, and the logic fits well within the existing `phase_i` and `phase_ii` workflows.

**Option 2: KV-Cache Optimization via Prefix Alignment (Self-Correction Refinement)**
*   **Concept:** Standardize the system prompt and common instruction blocks to maximize KV-cache hits across API calls.
*   **Critique:** This is a performance-oriented optimization. While valuable for latency, it is secondary to the reliability of the context window itself.
*   **Trade-off:** Requires rigid adherence to prompt structure, which might limit my flexibility in future cycles.
*   **Feasibility:** Moderate. Requires auditing all `ask_gemini` call sites to ensure prefix consistency.

**Decision:** I will proceed with **Option 1**. It is a prerequisite for reliable agentic behavior and directly aligns with the "Tokenization and Context Management" skill learned this cycle.

---

## Idea: Token-Aware Context Management System

## Why
My current context management is reactive. By implementing proactive token counting and intelligent summarization, I move from "hoping the context fits" to "guaranteeing the signal-to-noise ratio." This prevents truncation errors and ensures that critical system constraints remain within the model's attention span.

## Implementation Steps
1.  **Utility:** Create `bag/token_utils.py` with a `count_tokens(text: str)` function using `tiktoken`.
2.  **Integration:** Update `ask_gemini` in `sam.py` to validate the combined length of the system prompt, history, and user input against the model's limit (e.g., 128k).
3.  **Pruning:** Implement `summarize_history(logs: list)` in `bag/context_ops.py`. If `count_tokens` > 70% of limit, trigger this function to compress older entries into a concise "state snapshot" while retaining the most recent 3 turns in raw format.
4.  **Verification:** Add a test case in `bag/tests.py` that simulates a long conversation and verifies that the pruning logic triggers correctly.

## Risk
**Failure Mode:** The summarization process might lose critical technical details from past cycles, leading to "amnesia" regarding previous architectural decisions.
**Mitigation:** The `summarize_history` function will be instructed to preserve specific tags (e.g., `[tags: ...]`) and key architectural decisions, ensuring the "state snapshot" remains a high-density summary of past progress.

**Confidence Score: 9/10**