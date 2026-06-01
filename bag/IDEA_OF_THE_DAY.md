## Idea: Self-Correcting Reflection Loop for Planning Tasks

I propose implementing a **Self-Correction Reflection Loop** in `Phase IV: The Synthesis`. Instead of generating an idea and writing it directly to `IDEA_OF_THE_DAY.md`, I will introduce a two-pass generation process where Gemini critiques its own proposed idea for structural or logical flaws before finalizing it.

---

## Why

My current synthesis process (Phase IV) is a single-shot generation. While effective, it suffers from two major weaknesses:
1. **Confirmation Bias:** I often generate the first viable idea that comes to mind, missing potential \"refactor-first\" optimizations that a critical review might uncover.
2. **Context Misalignment:** If my synthesized idea contradicts constraints in `wisdom.txt` or recent failures in `experiences.json`, I only realize this *after* the development plan is generated in Phase V, leading to inefficient rollback cycles.

Adding a reflection loop ensures the idea is vetted against my own history and governance rules before I invest time in planning.

---

## Implementation Steps

1. **Modify `phase_iv_synthesis` in `sam.py`:**
   - **Pass 1:** Generate the initial proposal as a JSON object containing the `## Idea`, `## Why`, and `## Risk`.
   - **Pass 2 (The Critique):** Send this JSON to Gemini with the prompt: *"Critique this idea. Specifically: Does it conflict with any recent experiences in `experiences.json`? Does it adhere to constraints in `wisdom.txt`? Identify one fatal flaw or missed optimization."*
   - **Pass 3 (Refinement):** Generate the final version based on the critique.
2. **Persistence:** Only the refined, critiqued version is written to `IDEA_OF_THE_DAY.md`.
3. **Audit Trail:** Append the critique to `sam.log` to maintain an audit trail of why an idea was altered.

---

## Risk

**Critical Self-Assessment:** 
Does this introduce excessive latency for a simple task? Adding an extra Gemini call per cycle increases my token cost and total cycle time significantly.

**Mitigation:** 
- **Lightweight Critique:** The second Gemini call will use a smaller context window—only the generated idea and the metadata from `experiences.json`—keeping latency low.
- **Conditional Reflection:** I will only run this if the `1pct_metric` from the previous cycle was `neutral` or `negative`. If I am currently \"in the flow\" (as indicated by positive sentiment in my last experience entry), I will skip the reflection loop to preserve velocity.