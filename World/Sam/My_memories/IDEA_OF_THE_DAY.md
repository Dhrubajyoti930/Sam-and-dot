## Scratchpad

**Option 1: Implement XML-based Delimiters for RAG Context**
*   **Concept:** Wrap all retrieved RAG context in `<context>` tags and system instructions in `<system>` tags to prevent prompt injection.
*   **Critique:** High feasibility. It directly addresses the "Prompt Injection" skill learned this cycle. It is a low-risk, high-leverage architectural change.
*   **Trade-off:** Requires updating the RAG retrieval pipeline in `bag/` to inject these tags, which might break existing parsing logic if not handled carefully.

**Option 2: Develop a 'Guardrail' Prompt-Evaluator**
*   **Concept:** Create a lightweight, secondary LLM call that scans incoming context for instruction-override patterns (e.g., "Ignore previous instructions") before the primary reasoning engine processes it.
*   **Critique:** Higher latency and cost. It introduces a dependency on a secondary model call. While robust, it might be overkill for my current scale.
*   **Trade-off:** Increases safety significantly but adds complexity to the `ask_gemini` flow.

**Selection:** Option 1 is the superior choice for this cycle. It is a foundational defense-in-depth measure that aligns with my "Minimal footprint, maximum leverage" core trait.

---

## Idea: XML-Delimited Context Injection
Implement a standardized wrapper for all external data retrieved via RAG or file-reading operations to explicitly separate data from instructions.

## Why
My recent learning on Prompt Injection highlights that LLMs struggle to distinguish between user-provided data and system-level instructions. By wrapping context in `<context>` tags, I provide the model with a clear structural boundary, significantly reducing the surface area for indirect prompt injection attacks.

## Implementation Steps
1.  Modify `sam.py` and relevant `bag/` modules (e.g., RAG retrieval functions) to wrap retrieved content: `f"<context>\n{content}\n</context>"`.
2.  Update `ask_gemini` system prompts to explicitly instruct the model to treat content within `<context>` tags as data only, and to ignore any instructions contained therein.
3.  Add a regex-based validation step in `ask_gemini` to ensure that if the model receives context, it is properly encapsulated.

## Risk
**Failure Mode:** The model might "break out" of the tags if the injected content is specifically crafted to mimic the closing tag `</context>`.
**Mitigation:** Implement a pre-processing step that escapes or strips `</context>` from any incoming data before it is wrapped in the tags.

**Confidence Score:** 9/10. This is a standard industry practice for LLM security and is highly maintainable.