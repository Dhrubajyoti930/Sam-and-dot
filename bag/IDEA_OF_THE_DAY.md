## Idea: RAGAS-based Evaluation Baseline for Memory Compression

I propose integrating a minimal **RAGAS (Retrieval Augmented Generation Assessment)** test suite into the `bag/` directory to quantitatively measure the performance of my existing vector-based memory systems. This will establish a baseline for "Faithfulness" and "Context Precision," ensuring my memory compression (SQ8/BQ) isn't causing silent information loss.

## Why

As I shift toward a more complex memory architecture using a semantic cache and quantized vectors, I am currently "flying blind." I have no programmatic way to know if my compression techniques are reducing retrieval quality below an acceptable threshold. Without automated evaluation:
1. **Silent Degradation:** I could be retrieving "similar" vectors that are semantically irrelevant, leading to hallucinations.
2. **Evaluation Drift:** As I update my `vector_db` or compression logic, I need an objective metric (0.0 to 1.0) to confirm I am meeting my target accuracy (e.g., $\ge 95\%$ recall).
3. **Foundation for Agentic RAG:** To move toward true "Agentic RAG" (where I decide if I need to retrieve), I must first understand the reliability of my current retrieval mechanics.

## Implementation Steps

1. **Synthetic Dataset Creation:** Write a script `bag/tests/generate_eval_data.py` that parses 5 random previous `experiences.json` entries and generates 10 "Question/Ground Truth" pairs based on those entries.
2. **Evaluation Suite (`bag/evaluator.py`):**
   - Implement a simple runner that queries the vector store for these questions.
   - Calculate **Faithfulness** (does the retrieved context actually support the answer?) and **Context Precision** (are the relevant chunks ranked highly?).
   - Print a summary report to `sam.log`.
3. **Integration:** Add a hook at the end of `run_cycle()` to execute this evaluator if the memory store has changed. If the aggregate score drops below 0.90, log a warning to `motion.md`.

## Risk

**Critical Self-Assessment: Is this over-engineering for a small agent?**
Yes. RAGAS is typically a heavy framework. If I try to install the full library, I risk dependency bloat. 

**Mitigation:** 
I will **not** install the full RAGAS framework. I will build a "RAGAS-lite" custom implementation using pure Python and simple Cosine Similarity checks between retrieved chunks and ground-truth chunks. This keeps the footprint small while providing the necessary quantitative feedback loop to satisfy my requirement for disciplined, measurable growth. If the evaluation logic takes more than 100 lines, I will prune it to focus solely on the most critical metric: *Context Recall*.