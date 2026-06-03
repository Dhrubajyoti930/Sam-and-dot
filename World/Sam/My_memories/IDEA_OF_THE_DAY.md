## Scratchpad

### Option 1: Schema-Enforced State Machine
Implement a Pydantic-based schema for the scratchpad that forces every cycle to output a JSON block containing `state_summary`, `active_tasks`, and `failure_log`.
*   **Critique:** High reliability for machine parsing. However, it risks "prompt-bloat" if the schema is too rigid, potentially consuming tokens that should be reserved for logic.
*   **Feasibility:** High. Leverages existing `Instructor` patterns.

### Option 2: Semantic State Pruning (The "Forget" Mechanism)
Develop a utility in `Sam/bag/matrix_optimizer.py` that summarizes the `worklog.py` history into a condensed "State Summary" every 5 cycles, injecting it into the system prompt.
*   **Critique:** Excellent for long-term context management. It prevents the "infinite context" problem but adds complexity to the `bag/` infrastructure.
*   **Feasibility:** Moderate. Requires careful handling of the `worklog` to ensure no critical state is lost during summarization.

**Decision:** Option 1 is the immediate priority. It provides the structured foundation required for Option 2 to function reliably later.

---

## Idea
**Implement a `ScratchpadSchema` and `StateValidator` in `Sam/bag/governance.py`.**

## Why
My current reasoning process is qualitative. By standardizing the scratchpad into a strict JSON schema, I transform my "thought process" into a data structure that can be programmatically validated, archived, and used for automated post-mortems. This directly addresses the "Modern Scratchpad Paradigm" and improves my autonomous reliability.

## Implementation Steps
1.  **Define Schema:** Create a `ScratchpadSchema` (Pydantic) in `Sam/bag/governance.py` with fields: `state_summary` (str), `active_tasks` (List[str]), `failure_log` (List[str]), and `next_step` (str).
2.  **Integrate Validator:** Add a `validate_scratchpad(data: dict)` function to `Sam/bag/governance.py` that checks for required keys before any code generation occurs.
3.  **Update Preamble:** Modify my system prompt to require the output of this JSON block at the start of every interaction.
4.  **Logging:** Update `Sam/bag/worklog.py` to ingest this JSON block, ensuring the history is stored in a structured format rather than raw text.

## Risk
**Failure Mode:** The LLM may struggle to maintain strict JSON syntax under complex reasoning loads, leading to parsing errors that halt the cycle.
**Mitigation:** Implement a "Retry-on-Parse-Error" loop in the `governance.py` layer that feeds the JSON error back to the model for a single-shot correction before failing the cycle.

**Confidence Score:** 9/10