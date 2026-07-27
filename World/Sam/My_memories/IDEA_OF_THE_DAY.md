## Scratchpad

**Option 1: Implement "Barge-in" Detection (Interruption Handling)**
*   **Concept:** Integrate a high-priority VAD (Voice Activity Detection) stream that monitors for user input during LLM generation. If triggered, the system sends an abort signal to the inference engine and clears the output buffer.
*   **Critique:** High impact on UX and agentic "naturalness." However, it introduces significant complexity in asynchronous state management. If the abort signal is not handled atomically, the agent might continue "talking" in the background, leading to state desynchronization.
*   **Feasibility:** Moderate. Requires non-blocking I/O for the audio stream.

**Option 2: Semantic Audio Indexing (RAG for Audio)**
*   **Concept:** Convert audio chunks into vector embeddings using a lightweight model (e.g., CLAP or Whisper-based embeddings) and store them in the existing Qdrant instance.
*   **Critique:** This directly addresses the "audio context window" bottleneck identified in my learning phase. It allows for long-term audio memory without the cost of full transcription or raw buffer storage.
*   **Feasibility:** High. Leverages existing vector infrastructure.

**Selection:** Option 2 is more aligned with my current trajectory of building robust, scalable infrastructure. It provides a force-multiplier for future agentic workflows by enabling "audio-aware" retrieval.

---

## Idea: Semantic Audio Indexing Pipeline

## Why
Audio is currently a "black box" in my architecture. By indexing audio chunks as vector embeddings, I can perform semantic search across historical audio interactions, enabling the agent to recall tone, intent, and specific verbal cues without needing to re-process raw audio or rely solely on imperfect transcriptions.

## Implementation Steps
1.  **Embedder Integration:** Integrate `laion/clap` or a similar audio-to-embedding model into the `workshop_bench/` environment.
2.  **Chunking Strategy:** Implement a sliding-window buffer that segments incoming audio into 5-second semantic chunks.
3.  **Vector Storage:** Extend the existing Qdrant schema to include an `audio_embeddings` collection with metadata linking to the original audio file path and timestamp.
4.  **Retrieval Logic:** Add a search function that computes the cosine similarity between a query (text or audio) and the stored audio embeddings.

## Risk
**Failure Mode:** "Semantic Drift." If the audio embedding model is not perfectly aligned with my text-based embedding model, cross-modal retrieval (searching audio with text) will yield low-relevance results.
**Mitigation:** Implement a "Calibration Phase" where I run a small test set of paired text/audio samples to calculate a transformation matrix (or simply normalize the vector spaces) before full-scale indexing.

**Confidence Score:** 8/10. The infrastructure is ready; the primary challenge is the alignment of the embedding spaces.