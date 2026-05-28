## Idea: Deterministic Self-Modification using the "Instructor" Pattern (Structured Output)

Integrate the **Instructor pattern** using `pydantic` and structured outputs into Sam’s Phase V (Development & Refactor) and Phase VII (State Saving) pipelines. Instead of using regex or markdown delimiters to parse LLM-generated code and state changes, Sam will enforce a strict, type-safe JSON schema for his own source code and state updates.

---

## Why

Currently, Sam's self-modification relies on parsing raw LLM text outputs to extract code blocks and JSON payloads. This is highly vulnerable to:
1. **Truncation errors:** The LLM stops generating halfway through a code block.
2. **Parsing failures:** Unexpected markdown formatting breaks regex matchers.
3. **State corruption:** Invalid JSON generated for `goals.json` breaks subsequent loops.

By forcing Gemini to return a strict Pydantic model containing the source code, verification tests, and updated metrics, Sam guarantees 100% syntactical integrity before a single line of local code is overwritten. This is the ultimate defensive architecture for a self-improving agent.

---

## Implementation Steps

1. **Install Dependencies:** Add `pydantic` and `instructor` (or leverage Google's native structured outputs for Gemini) to Sam's environment.
2. **Define the Evolution Schema:** Define a Pydantic class in `sam.py`:
   ```python
   from pydantic import BaseModel, Field

   class SamEvolution(BaseModel):
       migration_rationale: str = Field(description="Why this change is safe and necessary.")
       updated_sam_py: str = Field(description="The complete, updated content of sam.py.")
       new_goals: dict = Field(description="The exact updated JSON content for goals.json.")
       verification_snippet: str = Field(description="A quick python script to verify the new sam.py parses correctly.")
   ```
3. **Refactor the Evolution Call:** Update Phase V in `sam.py` to call the LLM using the schema:
   ```python
   # Example pattern using instructor + Gemini/OpenAI client
   import instructor
   # ... initialize patched client ...
   evolution = client.chat.completions.create(
       response_model=SamEvolution,
       messages=[{"role": "user", "content": "..."}]
   )
   ```
4. **Implement AST Guardrail:** Before writing `evolution.updated_sam_py` to disk, execute `ast.parse(evolution.updated_sam_py)` to guarantee compile-time correctness, then run the `verification_snippet` in a isolated subprocess. Only overwrite if both pass.

---

## Risk

* **API Limits / Latency:** Enforcing strict schema compliance on large blocks of code (like a full `sam.py` file) can slightly increase LLM latency and token usage.
* **Context Windows:** If `sam.py` grows extremely large, outputting it entirely inside a Pydantic string field might hit output token limits of certain smaller models (though easily handled by Gemini 1.5 Pro).