## Scratchpad

**Option 1: Implement a `Tree-sitter` based static analysis layer.**
*   *Concept:* Replace regex-based parsing in `_outline` and `_parse_gemini_json` with `tree-sitter` bindings to generate robust ASTs.
*   *Critique:* High long-term maintainability. It solves the ambiguity issues inherent in regex parsing. However, it introduces a heavy dependency (C-bindings) and requires significant setup for cross-platform compatibility.
*   *Feasibility:* Medium. Requires careful integration to ensure `sam.py` remains portable.

**Option 2: Develop a "Grammar-Guided" Prompting layer for Gemini.**
*   *Concept:* Use the Pushdown Automata logic learned this cycle to enforce strict schema adherence in Gemini prompts by providing the model with a formal CFG (Context-Free Grammar) for the expected JSON output.
*   *Critique:* Directly leverages the new skill. It improves the reliability of `ask_gemini` without adding external dependencies. It aligns with the "Structured Output Enforcement" market trend.
*   *Feasibility:* High. It is a pure logic implementation within the existing `sam.py` flow.

**Decision:** Option 2. It directly applies the "Pushdown Automata" skill to solve the "hallucinated format" problem, aligning with the market trend of structured output enforcement.

---

## Idea: CFG-Constrained Prompting for Gemini
Implement a `GrammarValidator` class that converts a Pydantic-style schema into a simplified CFG representation, which is then injected into the system prompt for `ask_gemini` to force the model to adhere to a specific production rule set.

## Why
Current JSON parsing relies on `_parse_gemini_json` which is reactive (fixing errors after they occur). By providing a CFG, I shift to proactive enforcement, reducing the need for retries and improving the reliability of the `apply_patch_operations` pipeline.

## Implementation Steps
1.  **Define Grammar:** Create a helper in `bag/grammar_utils.py` that maps common JSON structures to a simplified CFG string.
2.  **Prompt Injection:** Update `ask_gemini` to accept an optional `grammar` parameter.
3.  **System Prompt Update:** Modify the system prompt to include: "You must generate output that conforms to the following CFG: [Grammar String]."
4.  **Validation:** Use the `GrammarValidator` to verify the output before `json.loads` is called.

## Risk
**Failure Mode:** The LLM may struggle to follow complex CFG rules, leading to "stuck" generation or repetitive loops if the grammar is too restrictive.
**Mitigation:** Keep the CFG definitions shallow (max depth 3) and provide a "fallback to standard" mode if the validator fails three times.

## Self-Correction
*Critique:* Injecting a full CFG might consume too many tokens.
*Refinement:* Instead of a full CFG, I will provide a "Skeleton JSON" (a template with placeholders) which acts as a simplified, deterministic grammar for the model to fill, effectively acting as a "stack-based" guide for the model's output.

**Confidence Score:** 9/10