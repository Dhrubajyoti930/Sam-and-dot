## Scratchpad

**Option 1: Implement `pgvector` for Semantic Memory**
*   **Concept:** Replace the current `semantic_cache` (which relies on local JSON/files) with a `pgvector` integration in the `bag/` directory.
*   **Critique:** High leverage for long-term memory, but introduces a heavy dependency (Postgres). It violates my "minimal footprint" principle if I have to manage a database service.
*   **Feasibility:** Moderate. Requires setting up a containerized Postgres instance, which might complicate the `workshop_bench` environment.

**Option 2: Automated "Agentic RAG" for `bag/` documentation**
*   **Concept:** Create a tool that indexes my `bag/` documentation and `experiences.json` using a local embedding model (via Ollama), allowing me to query my own history during `phase_iv_synthesis`.
*   **Critique:** Directly addresses the "Agentic Workflows" market signal. It improves the quality of my synthesis by grounding it in past successes/failures.
*   **Feasibility:** High. I can use `instructor` for structured output and `Ollama` for local embeddings. It keeps the footprint small by using local tools.

**Selection:** Option 2. It aligns with the "Agentic Workflows" and "Localized LLM" market signals while directly improving my internal reasoning capabilities.

---

## Idea: Localized Semantic Retrieval for Self-Reflection

Implement a lightweight, local RAG utility in `bag/` that embeds my `experiences.json` and `knowledge_log.json` using a local Ollama embedding model. This will allow me to perform a "semantic search" during `phase_iv_synthesis` to ensure my new ideas are truly novel and build upon past learnings rather than just repeating them.

## Why
I am currently relying on manual review of recent experiences. As my history grows, this becomes inefficient. An agentic retrieval step will allow me to cross-reference my proposed ideas against my entire history of successes and failures, ensuring higher-quality, non-redundant output.

## Implementation Steps
1.  **Dependency:** Add `ollama` and `instructor` to the environment.
2.  **Indexing:** Create `bag/memory_indexer.py` to generate embeddings for `experiences.json` and `knowledge_log.json` using `nomic-embed-text` (via Ollama).
3.  **Retrieval:** Add a `search_memory(query: str)` function to `sam.py` that performs a cosine similarity check against the stored embeddings.
4.  **Integration:** Update `phase_iv_synthesis` to call `search_memory` before finalizing the `IDEA_OF_THE_DAY.md`.

## Risk
**Failure Mode:** The local embedding model might return irrelevant results if the query is too broad, leading to "hallucinated" connections between unrelated past experiences.
**Mitigation:** Implement a strict similarity threshold (e.g., > 0.75) and a fallback to the existing manual review if no high-confidence matches are found.

**Confidence Score: 8/10** (The logic is sound, but local model latency during `phase_iv` needs to be monitored to ensure it doesn't exceed the `_CALL_DELAY` budget).