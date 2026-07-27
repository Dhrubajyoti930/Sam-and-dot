## Scratchpad

**Option 1: FIM-Aware Prompt Templating**
*   **Concept:** Modify `ask_gemini` to detect if the prompt is a code-completion task and inject FIM sentinel tokens (`<PRE>`, `<SUF>`, `<MID>`) based on the surrounding context of the target file.
*   **Critique:** High utility for refactoring. However, it requires robust parsing of the "suffix" (the code following the insertion point). If the suffix is malformed or spans across complex scope boundaries, the model might hallucinate syntax to "close" the block, leading to invalid code.
*   **Feasibility:** High. I have the `_outline` and `apply_patch_operations` infrastructure to identify insertion points.

**Option 2: Context-Weighting via Semantic Summarization**
*   **Concept:** Instead of passing raw code blocks, generate a "semantic skeleton" (docstrings, type hints, and function signatures) of the prefix and suffix to provide the model with structural anchors without overwhelming the attention window.
*   **Critique:** This addresses the "Infilling Bias" identified in my self-correction. It reduces token usage and improves focus. The risk is that the model might miss subtle logic dependencies that aren't captured in the skeleton.
*   **Feasibility:** Moderate. Requires a reliable AST-based summarizer.

**Selection:** I will proceed with **Option 1 (FIM-Aware Prompting)** as the primary implementation, but I will incorporate **Option 2 (Semantic Anchoring)** as the method for defining the "Prefix" and "Suffix" inputs to ensure the model remains grounded.

---

## Idea: FIM-Integrated Surgical Patching
Implement a `prepare_fim_prompt` utility that wraps code-patching requests in FIM sentinel tokens, using AST-extracted signatures as the "Prefix" and "Suffix" anchors to guide the model's completion.

## Why
Standard prompting often leads to "drift" when inserting code into existing functions. By explicitly defining the boundary with `<PRE>` and `<SUF>` tokens, I force the model to respect the existing scope and type constraints, significantly reducing the need for corrective linting passes.

## Implementation Steps
1.  **Update `bag/patch_ops.py`**: Add a helper to extract the 5 lines preceding and following an insertion point.
2.  **Modify `ask_gemini`**: Add a `fim_mode` parameter that formats the prompt using `<PRE> {prefix} <SUF> {suffix} <MID>`.
3.  **Validation**: Update `_dry_run_lint` to specifically check the generated block for structural integrity before applying the patch.

## Risk
**Failure Mode:** The model may fail to generate the correct number of closing braces or indentation levels if the suffix context is too short or ambiguous.
**Mitigation:** I will implement a "Brace-Balance Check" in the validation logic that compares the open/close counts of the generated block against the surrounding scope.

**Confidence Score:** 8/10