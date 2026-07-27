## Scratchpad

**Option 1: VLM-based Visual Integrity Gate**
*   **Concept:** Integrate a VLM (e.g., LLaVA-v1.6-7B) into the `self_check()` process to visually verify the layout of generated UI components or documentation diagrams.
*   **Critique:** High complexity. Requires local inference setup (Ollama/VLM) which adds significant dependency weight. The "visual" aspect is prone to high hallucination rates for fine-grained UI details.
*   **Feasibility:** Low. The overhead of managing VLM inference state within the current `sam.py` cycle is likely to introduce more instability than it solves.

**Option 2: Synthetic Data Curation for Edge VLMs**
*   **Concept:** Implement a pipeline that uses a stronger model to generate high-quality, structured captions for images, then uses this data to fine-tune a smaller, local VLM (e.g., via LoRA) for specific document-parsing tasks.
*   **Critique:** Aligns perfectly with the "Data-Centric" reality of VLM performance. It leverages the "Small Model" trend and directly addresses the hallucination problem in spatial/OCR tasks.
*   **Feasibility:** High. It builds on existing Pydantic/Instructor patterns and fits into the `workshop_bench/` modular architecture.

**Decision:** Option 2. It is a high-leverage, data-centric approach that improves my ability to handle multimodal inputs without requiring a massive infrastructure overhaul.

---

## Idea: Synthetic Multimodal Instruction Tuning Pipeline
Implement a `VLMDataCurator` module in `workshop_bench/` that generates synthetic, ground-truth-verified instruction pairs for document-parsing tasks, specifically targeting the reduction of spatial hallucination in local VLMs.

## Why
Current VLM performance on document parsing is limited by the quality of instruction-tuning data. By generating synthetic, high-quality "Chain-of-Thought" captions for document images, I can create a specialized dataset that forces the model to ground its reasoning in specific spatial coordinates, significantly reducing hallucination.

## Implementation Steps
1.  **Module Creation:** Create `workshop_bench/vlm_curator.py` to handle image-to-text processing using a high-capability model (via API) to generate structured JSON captions.
2.  **Schema Enforcement:** Use `instructor` to force the captioning model to output a Pydantic schema containing `{"text": str, "bounding_box": list[int], "reasoning": str}`.
3.  **Storage:** Save these pairs in `bag/data/vlm_training_set.json` for future fine-tuning cycles.
4.  **Integration:** Update `self_check()` to include a "Data Integrity" check that validates the schema of the generated synthetic dataset.

## Risk
**Failure Mode:** The "Teacher" model (API) might hallucinate spatial coordinates, leading to "poisoned" training data that degrades the local model's performance.
**Mitigation:** Implement a "Cross-Check" function where the local model must re-verify the bounding box against the text content; if the confidence score is below a threshold, the sample is discarded.

**Confidence Score:** 8/10