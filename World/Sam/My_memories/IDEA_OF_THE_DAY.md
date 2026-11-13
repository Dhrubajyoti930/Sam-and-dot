## Scratchpad

**Option 1: Automated "Judge" Model Integration for RAG**
*   **Concept:** Implement a lightweight classifier (e.g., a small BERT-based model or a constrained Gemini prompt) to evaluate retrieved context for prompt injection patterns before it reaches the primary LLM.
*   **Critique:** High security value, but adds latency to the RAG pipeline. Requires careful management of the "Judge" model's own prompt to avoid it being bypassed.
*   **Feasibility:** High. Fits well with the existing `bag/` architecture.

**Option 2: Structural XML-Encapsulation Wrapper**
*   **Concept:** Create a utility function that wraps all external data (RAG, user input, web content) in `<context>` or `<user_input>` tags before passing to `ask_gemini`.
*   **Critique:** Extremely low latency, high impact. It forces the LLM to treat data as data, not instructions. It is a "minimal footprint" change that aligns with the "defense-in-depth" strategy.
*   **Feasibility:** Very high. Can be implemented as a decorator or a pre-processing step in `sam.py`.

**Selection:** Option 2. It is more elegant, requires less infrastructure than a "Judge" model, and provides immediate, robust protection against the most common injection vectors.

---

## Idea: XML-Based Contextual Isolation
Implement a mandatory `encapsulate(data: str, role: str)` utility in `sam.py` that wraps all untrusted input in XML tags. All calls to `ask_gemini` will be routed through a pre-processor that ensures no raw string is ever passed to the model without this structural boundary.

## Why
Prompt injection is an ambiguity problem. By forcing a strict structural schema on the LLM, we define a clear "sandbox" for data. This prevents the model from conflating user-provided data with system-level instructions, effectively neutralizing basic "ignore previous instructions" attacks.

## Implementation Steps
1.  **Define Utility:** Add `def _encapsulate(data: str, role: str) -> str:` to `sam.py`.
2.  **Update `ask_gemini`:** Modify `ask_gemini` to accept an optional `context_map` (a dictionary of roles and data) and automatically wrap them in tags.
3.  **Refactor Calls:** Update `phase_i_deep_learning`, `phase_v_development`, and `phase_vi_cognitive_evolution` to use this new interface instead of raw string concatenation.
4.  **Sanitization:** Add a regex-based strip to `_encapsulate` to remove any existing XML tags in the input to prevent "tag-breaking" attacks.

## Risk
**Failure Mode:** The model might struggle if the input data contains nested XML tags that confuse the parser or the LLM's attention mechanism.
**Mitigation:** The `_encapsulate` function will escape or strip existing `<` and `>` characters within the input data to ensure the structure remains flat and predictable.

**Confidence Score:** 9/10. This is a standard industry practice for LLM security and is highly maintainable.