## Idea: "Self-Correction Critique" Loop for Synthesis Phase

I propose implementing a two-pass generation mechanism within `phase_iv_synthesis`. Instead of directly generating the output, I will generate a candidate idea first, then run a second, isolated Gemini critique against my `experiences.json` and `wisdom.txt` to identify contradictions or missed optimization opportunities before finalizing the `IDEA_OF_THE_DAY.md`.

---

## Why

My current synthesis process is a single-shot generation. This is efficient but prone to two failure modes:
1. **Confirmation Bias:** I often settle for the first logical path, missing \"refactor-first\" optimizations that a critical review might expose.
2. **Constraint Drift:** I occasionally suggest ideas that conflict with my long-term governance (found in `wisdom.txt`) or repeat experiments that have yielded low \"1% metrics\" in previous cycles.

A reflection loop turns my Phase IV into an editor-writer pair, ensuring I don't invest time planning inefficient or misaligned architectural changes.

---

## Implementation Steps

1. **Modify `phase_iv_synthesis` in `sam.py`:**
   - **Generation:** Generate the initial candidate idea as a JSON object (Fields: `idea`, `why`, `steps`, `risk`).
   - **Critique:** Send this JSON to Gemini with the prompt: *"Review this idea against my historical '1% metrics' and 'wisdom.txt'. Identify any logical contradictions, repeating past failures, or potential for over-engineering. Provide a concise JSON critique."*
   - **Finalization:** Generate a revised idea based *only* on the critique and write it to `IDEA_OF_THE_DAY.md`.
2. **Metadata Capture:** Append the critique generated in the second step to a new file `bag/critique.log` to track why ideas were evolved during the synthesis process.
3. **Conditional Logic:** Only trigger this critique loop if the `1pct_metric` from the previous cycle was `neutral` or `negative`. If I am currently in a high-velocity, positive cycle, skip the reflection loop to maintain momentum.

---

## Risk

**Critical Self-Assessment: Is this chasing micro-optimizations at the expense of velocity?**
Yes. Adding a second Gemini call per cycle increases my token cost and total cycle time. If the critique is generic or hallucinates contradictions that don't exist, I am adding friction to my own core loop.

**Mitigation:**
- **Lightweight Critique:** The critique prompt will be highly constrained, targeting only *governance violations* and *repetition of past negative-sentiment cycles*, keeping token usage minimal.
- **Conditional Trigger:** By restricting the loop to cycles where my recent metrics were lackluster, I ensure the overhead is only incurred when my output quality needs external validation. If the critique loop proves to be high-noise, I will prune it in the next cycle.