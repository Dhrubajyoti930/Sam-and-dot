## Scratchpad

**Option 1: Atomic Claim Extraction & NLI Verification Pipeline**
*   **Concept:** Implement a module that decomposes LLM output into atomic propositions and uses a `DeBERTa-v3-large` NLI head to verify entailment against retrieved context.
*   **Critique:** High technical alignment with current market trends (Factual Grounding). It addresses the "black-box" hallucination problem directly.
*   **Trade-offs:** Significant latency increase due to secondary model inference. Requires managing a separate model lifecycle within the `workshop_bench/`.
*   **Feasibility:** High. The logic is well-defined in the cycle's technical summary.

**Option 2: CoT Faithfulness Verification (Logical Grounding)**
*   **Concept:** Implement a "Verify-then-Generate" loop where the model must output its reasoning steps as a directed acyclic graph (DAG) and validate each edge against the source context.
*   **Critique:** Addresses the "hallucination of reasoning" weakness identified in my self-correction.
*   **Trade-offs:** Extremely complex to implement without a dedicated graph-processing library. High risk of "over-engineering" the prompt chain.
*   **Feasibility:** Moderate. Requires more robust prompt engineering than Option 1.

**Selection:** Option 1 is more foundational. I must establish the "auditor" pattern (NLI verification) before I can reliably audit the "reasoning" (Option 2). I will proceed with the Atomic Claim Extractor.

---

## Idea: Atomic Claim Verification Engine (ACVE)

Implement a lightweight, Pydantic-driven atomic claim extractor and an NLI-based entailment auditor to serve as a factual gatekeeper for generated content.

## Why
Current RAG pipelines rely on semantic similarity, which is prone to "hallucination of detail." By decomposing output into atomic claims and verifying them against the retrieved premise using a specialized NLI model, I move from probabilistic generation to verifiable grounding. This directly addresses the industry shift toward "white-box" verification.

## Implementation Steps
1.  **Schema Definition:** Create `bag/models/claims.py` with a Pydantic `AtomicClaim` model (claim text, source_id, confidence_score).
2.  **Extractor:** Develop a prompt-based extractor in `workshop_bench/claim_extractor.py` that breaks down long-form text into a list of `AtomicClaim` objects.
3.  **Auditor:** Integrate a `transformers` pipeline using `cross-encoder/nli-deberta-v3-base` in `workshop_bench/nli_auditor.py` to score entailment.
4.  **Integration:** Update the generation loop to pass output through the `ACVE` before final delivery.

## Risk
**Failure Mode:** The "Atomic Claim Extractor" itself may hallucinate claims or fail to map them to the correct source, leading to false negatives in the NLI auditor.
**Mitigation:** Implement a "Confidence Threshold" (0.85). If the NLI auditor returns a low score, the system will trigger a `SelfCheckGPT` variance check (generating a second sample) to determine if the claim is truly unsupported or just poorly extracted.

**Confidence Score:** 8/10. The logic is sound, but the latency impact of running DeBERTa-v3-large requires careful asynchronous handling.