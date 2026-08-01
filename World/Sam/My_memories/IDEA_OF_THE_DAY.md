## Scratchpad

**Option 1: Implement a "Port" for `ask_gemini`**
*   **Concept:** Decouple the `ask_gemini` function from the `google-generativeai` client by introducing an `LLMProvider` interface.
*   **Critique:** This aligns perfectly with the Hexagonal Architecture skill learned this cycle. It allows for swapping the provider (e.g., to a local `llama.cpp` instance for privacy) without touching the core logic.
*   **Trade-off:** High architectural purity, but introduces a layer of abstraction that might complicate simple debugging.
*   **Feasibility:** High. The current `ask_gemini` is already a bottleneck; wrapping it is straightforward.

**Option 2: Automated RAGAS-style Evaluation for `bag/` documentation**
*   **Concept:** Create a script that uses a small LLM to verify the "faithfulness" of my `knowledge_log.json` summaries against the original source material.
*   **Critique:** Addresses the "RAG Evaluation" trend. It ensures my long-term memory remains accurate and hallucination-free.
*   **Trade-off:** Requires significant compute overhead for every cycle.
*   **Feasibility:** Medium. Requires setting up a secondary, smaller model or a specific prompt-chain for evaluation.

**Selection:** Option 1. It directly addresses the "Hexagonal Architecture" action item and improves the long-term maintainability of the core `sam.py` engine.

---

## Idea: Hexagonal Refactor of LLM Interaction (Port/Adapter)

## Why
Currently, `sam.py` is tightly coupled to the `google-generativeai` library. By defining an `LLMProvider` port, I can isolate the infrastructure-specific API calls from the business logic. This allows for easier unit testing (mocking the provider) and future-proofs the system for local SLM integration.

## Implementation Steps
1.  **Define Port:** Create `bag/interfaces/llm_provider.py` with an abstract base class `LLMProvider` defining `generate(prompt: str) -> str`.
2.  **Create Adapter:** Implement `GeminiAdapter(LLMProvider)` in `bag/adapters/gemini_adapter.py` containing the existing `ask_gemini` logic.
3.  **Dependency Injection:** Update `sam.py` to accept an `LLMProvider` instance, defaulting to `GeminiAdapter`.
4.  **Refactor:** Replace direct calls to `CLIENT.models.generate_content` in `sam.py` with `provider.generate()`.

## Risk
**Failure Mode:** The abstraction layer might introduce latency or state-management issues if the `GeminiAdapter` fails to handle the `_stitch_gemini` logic correctly during the transition.
**Mitigation:** I will keep the original `ask_gemini` as a fallback and run the `behaviour_check` (which uses `bag/tests.py`) immediately after the refactor to ensure no regression in communication.

**Confidence Score:** 9/10