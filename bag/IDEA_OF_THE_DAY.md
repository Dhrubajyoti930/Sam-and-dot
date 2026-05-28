## Idea
Integrate **`instructor`** to enforce strict Pydantic schemas for Sam's core cognitive steps—specifically for **Phase IV (The Synthesis/Idea Generation)** and **Phase VII (State Saving to `goals.json`)**. 

Instead of relying on freeform LLM JSON parsing (which is prone to structural breakages), Sam will wrap his LLM client with `instructor` to guarantee that all generated goals, metrics, and self-modification proposals strictly adhere to structured Python schemas before they are written to disk or executed.

---

## Why
Self-improving loops are highly vulnerable to schema drift and syntax errors. If an LLM response during Phase VII generates malformed JSON for `goals.json`, or if Phase IV proposes an unstructured code change that violates Sam's state boundaries, the loop halts, requiring manual human intervention. 

By implementing `instructor`:
1. **Guaranteed State Integrity:** `goals.json` will never be corrupted because Pydantic will validate the schema at the runtime level before writing to disk.
2. **Reliable Tooling/APIs:** It allows Sam to safely expose his run metrics and operational logs to external observability tools in later phases.
3. **Resiliency via Auto-Retries:** `instructor` has built-in validation retry loops, meaning if the LLM produces an invalid schema, it self-corrects before completing the phase.

---

## Implementation Steps

1. **Dependency Update:** Add `instructor` and `pydantic` to Sam's setup requirements.
2. **Define Schemas:** Add two distinct Pydantic models to `sam.py`:
   * `GoalSchema`: Validates the structure of `goals.json` (e.g., fields for `current_cycle`, `metrics`, `strategic_objectives`, `last_run_status`).
   * `SynthesisSchema`: Validates Phase IV outputs (e.g., fields for `idea_title`, `rationale`, `affected_files`, `proposed_code`).
3. **Patch LLM Calls:** 
   * Import `instructor` and patch the LLM client (e.g., `client = instructor.from_openai(OpenAI())` or the equivalent Gemini/Anthropic client).
   * Update Phase IV and VII functions to use `response_model=GoalSchema` or `response_model=SynthesisSchema`.
4. **Validation Handling:** Implement a graceful fallback. If validation fails after maximum retries, Sam logs the error to a diagnostic file and falls back to his last known-good `goals.json` state rather than crashing.

---

## Risk
* **Token Overhead & Latency:** `instructor`'s automatic retry mechanism on validation failure can consume more API tokens and increase runtime latency.
* **Mitigation:** Set `max_retries=2` on the instructor client, and write highly explicit system prompts detailing the expected JSON output format to ensure the LLM succeeds on the first attempt 99% of the time.