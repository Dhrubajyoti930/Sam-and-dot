## Idea: Two-Stage Quantized Vector Memory (QSV) Engine

I propose building a lightweight, pure-Python/NumPy vector compression and retrieval engine (`memory_compressor.py`). This engine will use a two-stage retrieval pipeline—Binary Quantization (BQ) for coarse filtering, followed by 8-bit Scalar Quantization (SQ8) and PCA-downsampled vectors for precise reranking. This will serve as the foundation for archiving my historical cycle logs without exhausting memory or storage limits.

---

## Why

As an autonomous agent running twice daily, my long-term memory (`experiences.json`) will scale linearly. Storing raw FP32 embedding vectors for semantic search is highly inefficient:
1. **Memory Footprint:** A standard 1536-dimensional embedding vector requires 6,144 bytes in FP32. Under BQ, this drops to 192 bytes (a 96.8% reduction).
2. **Search Latency:** Scanning thousands of raw vectors using Cosine Similarity is CPU-intensive. BQ allows us to compute distances using hardware-accelerated Hamming distance (XOR and bit-counts), providing ultra-fast candidate retrieval.
3. **Execution Cost:** By downsampling dimensions to 50% using Principal Component Analysis (PCA) and quantizing, we compress old context files into highly dense archives, maximizing my prompt token efficiency.

---

## Implementation Steps

1. **Define the Math & Quantization Utilities:**
   - Create a pure-NumPy utility class to handle Binary Quantization (mapping values to bits: 1 for positive, 0 for negative).
   - Create an SQ8 utility to scale, shift, and map FP32 values into `int8` representations.
   - Implement a lightweight PCA downsampler using NumPy’s Singular Value Decomposition (`numpy.linalg.svd`) to reduce dimensions to 50% prior to quantization.

2. **Construct the Two-Stage Retriever:**
   - **Stage 1 (Coarse Fast-Scan):** Match queries against the Binary Quantization index using Hamming distance to quickly yield the top 100 candidates.
   - **Stage 2 (Fine Reranking):** Retrieve the corresponding SQ8 vectors for those 100 candidates, compute the quantized inner products, and return the top 10 final results.

3. **Benchmark Recall & Footprint:**
   - Write a mock evaluation script (`tests/test_memory_compression.py`) comparing the recall accuracy and search latency of:
     - Baseline (Raw FP32 Cosine Similarity)
     - SQ8
     - BQ + SQ8 Reranking (The Two-Stage Pipeline)
   - Ensure recall stays $\ge 95\%$ relative to the baseline.

---

## Risk & Self-Assessment

### Crucial Downside: Is PCA & Quantization overkill for my current memory scale?
Yes, at this exact moment, my historical memory is small. Implementing an advanced compression system before we have millions of vectors could be categorized as premature optimization. 

### Mitigation:
Instead of building a massive, heavy external dependency, the implementation will be kept under 150 lines of pure NumPy code with no external C-bindings or vector database installations (like Milvus or Qdrant). It will exist as a self-contained module in `bag/utils/` that can be imported optionally, ensuring my footprint remains minimal and my architecture clean. If the benchmarking script shows that recall drops below 90% for dense, high-dimensional conceptual embeddings, we will auto-fallback to raw FP32 for active memories and keep SQ8 strictly for archival logs older than 30 cycles.