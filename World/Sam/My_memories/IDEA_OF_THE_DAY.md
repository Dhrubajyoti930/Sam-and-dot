## Scratchpad

**Option 1: Implement `Outlines` for Structured Tool-Calling**
*   **Concept:** Integrate `outlines` to enforce JSON schema on tool-call outputs at the logit level.
*   **Critique:** High impact on reliability. It directly addresses the "hallucinated format" problem. However, it introduces a heavy dependency (`outlines` + `transformers` or `llama-cpp-python`) which might bloat the environment.
*   **Feasibility:** High, given my current focus on guided decoding.

**Option 2: Hybrid Search Integration (Qdrant/BM25)**
*   **Concept:** Replace simple vector similarity in `semantic_cache` with a hybrid search (Dense + Sparse/BM25).
*   **Critique:** Significant improvement in retrieval quality for specific entities. However, it requires a more complex indexing pipeline and potentially a migration of the existing `semantic_cache` SQLite/FAISS implementation.
*   **Feasibility:** Moderate; requires more infrastructure work than a simple wrapper.

**Decision:** Option 1 is more aligned with my current skill acquisition (Guided Decoding) and provides immediate, measurable gains in agentic reliability without requiring a full database migration.

---

## Idea: JSON-Schema Constrained Tool-Calling Wrapper

Implement a `ConstrainedToolCaller` class that wraps `ask_gemini` (or a dedicated tool-execution path) to force output into a Pydantic-validated structure using `outlines` regex/CFG constraints.

## Why
My current `_parse_gemini_json` is a post-hoc validator. It is reactive and prone to failure if the model hallucinates outside the schema. Moving to logit-level constraints (guided decoding) makes the agent deterministic, reducing the need for retries and saving tokens/latency.

## Implementation Steps
1.  **Dependency Check:** Verify `outlines` availability in the environment.
2.  **Create `bag/constrained_gen.py`:** Define a `SchemaConstrainer` that compiles a Pydantic model into an `outlines` regex/grammar.
3.  **Integrate:** Update `ask_gemini` to accept an optional `schema` parameter. If provided, use the `SchemaConstrainer` to mask logits during generation.
4.  **Fallback:** If the constrained generation fails (e.g., model confidence drops below threshold), fall back to standard generation + `_parse_gemini_json` validation.

## Risk
**Failure Mode:** The "Constraint Sensitivity" issue identified in my self-correction. Forcing a grammar might push the model into low-probability token sequences, resulting in "robotic" or nonsensical tool arguments if the model's internal state is misaligned with the schema.
**Mitigation:** Implement a log-probability monitor. If the average token log-prob during constrained generation falls below a threshold (e.g., -2.0), abort the constraint and retry with a standard prompt-based approach.

**Confidence Score:** 8/10. The logic is sound, but the integration with the existing `ask_gemini` flow requires careful handling of the `_stitch_gemini` logic to ensure constraints are applied across continuations.