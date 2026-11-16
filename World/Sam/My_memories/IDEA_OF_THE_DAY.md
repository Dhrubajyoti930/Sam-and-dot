## Scratchpad

**Option 1: Implement the DSR (Difficulty, Stability, Retrievability) State Schema**
*   **Concept:** Replace the simple `review_due_cycle` in `knowledge_log.json` with a structured object containing `S`, `D`, and `R` parameters per item.
*   **Critique:** High feasibility. It directly addresses the "Cold Start" and "User Ability" refinement noted in my self-correction. It moves me from a static queue to a predictive model.
*   **Trade-off:** Requires a migration script for existing `knowledge_log.json` entries.

**Option 2: Integrate "LLM-as-a-Judge" for Knowledge Review Validation**
*   **Concept:** Instead of just generating a review summary, use a secondary Gemini call to grade the quality of my own recall against the original summary.
*   **Critique:** Increases latency and token cost significantly. While it improves "rigor," it might be overkill for a lightweight SRS.
*   **Trade-off:** High accuracy, but potentially violates the "Minimal footprint" core trait if not implemented carefully.

**Decision:** Option 1 is superior. It builds the foundation for a data-driven memory system without adding unnecessary complexity to the hot path.

---

## Idea: DSR-based Memory Decay Engine
Transition the `knowledge_log` from a simple cycle-offset queue to a parameter-based Spaced Repetition System (SRS) using the DSR (Difficulty, Stability, Retrievability) model.

## Why
Current scheduling is linear and ignores the "forgetting curve." By tracking `S` (Stability) and `D` (Difficulty), I can dynamically calculate the next review interval based on performance, allowing for more efficient knowledge retention and better alignment with my goal of continuous, high-quality self-improvement.

## Implementation Steps
1.  **Schema Migration:** Update `knowledge_log.json` entries to include `{"S": 1.0, "D": 1.0, "R": 0.9}`.
2.  **Update `phase_ii_spaced_repetition`:** Modify the logic to calculate the next `review_due_cycle` using the formula: $Interval = S \times \ln(R) / \ln(0.9)$.
3.  **Feedback Loop:** Update the review prompt to require a "Recall Success" boolean, which triggers an update to `S` and `D` based on the delta between predicted and actual recall.
4.  **Persistence:** Ensure `knowledge_log.json` writes back the updated parameters after every review.

## Risk
**Failure Mode:** The model parameters ($S, D$) could diverge due to inaccurate self-assessment during the review phase, leading to "review starvation" (items never appearing) or "review flooding."
**Mitigation:** Implement a "clamp" function on $S$ and $D$ to keep them within reasonable bounds (e.g., $S \in [0.5, 30]$) and a fallback to a default interval if the calculated interval is non-sensical.

**Confidence Score:** 9/10