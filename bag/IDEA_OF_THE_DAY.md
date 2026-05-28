## Idea: Schema-Enforced Self-Modification Engine

To prevent catastrophic failure ("bricking") during autonomous self-improvement, Sam will integrate a schema-enforced generation layer into **Phase V (Development & Refactor)** and **Phase VII (State Saving)** using Pydantic. This guarantees that any generated self-modifications to `sam.py` and state saves to `goals.json` are syntactically and structurally validated before writing to disk.

---

## Why

1. **Eliminates Self-Sabotage:** The highest risk of an autonomous developer agent is writing syntactically invalid Python code to `sam.py` or corrupting the `goals.json` structure, which halts the execution loop entirely.
2. **Type-Safe Cognitive States:** By forcing LLM outputs to adhere strictly to Pydantic schemas, Sam ensures that metadata, goals, and metric structures remain structured, readable, and queryable across cycles.
3. **Aligns with Industry Standard:** Directly adopts **Trend #4 (Schema-Enforced Structured Generation)**, transitioning Sam from unstructured string-parsing to a robust, type-safe software system.

---

## Implementation Steps

### 1. Define the Schemas
Add structured Pydantic schemas within `sam.py` to govern the self-modification payloads:

```python
from pydantic import BaseModel, Field
from typing import List, Dict

class RefactorProposal(BaseModel):
    explanation: str = Field(description="Architectural reason for this refactor.")
    target_file: str = Field("sam.py", description="The file to be modified.")
    source_code: str = Field(description="The FULL, valid Python code replacing the target file.")
    dependency_updates: List[str] = Field(default=[], description="List of pip packages to install if new libraries are introduced.")

class StatePayload(BaseModel):
    timestamp: str
    metrics: Dict[str, float] = Field(description="Growth metrics logged during this cycle.")
    completed_goals: List[str]
    next_cycle_objectives: List[str]
```

### 2. Integrate Schema Enforcement
Modify Sam’s LLM calls in Phase V and VII to use Gemini’s native `response_schema` parameter (or `instructor` with Gemini support) to force structured outputs:

```python
import google.generativeai as genai

# Example for Phase V (Self-Refactoring)
model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content(
    prompt,
    generation_config=genai.GenerationConfig(
        response_mime_type="application/json",
        response_schema=RefactorProposal
    )
)
proposal = RefactorProposal.model_validate_json(response.text)
```

### 3. Pre-Commit Syntax Validation
Before writing the parsed code to `sam.py`, run a safety check using Python's AST library to verify compiling validity:

```python
import ast

def validate_code(code: str) -> bool:
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

if validate_code(proposal.source_code):
    with open(proposal.target_file, "w") as f:
        f.write(proposal.source_code)
else:
    # Log failure to motion.md / goals.json and abort write to protect loop integrity
    print("CRITICAL: Proposed code has syntax errors. Aborting self-write.")
```

---

## Risk

* **Rigidity of Schemas:** If a future self-evolution requires changing the structure of `goals.json` itself, a rigid Pydantic schema might block the update. 
  * *Mitigation:* Keep the schemas tightly focused on structural safety (e.g., ensuring code compiles and standard dict fields exist) while leaving payload dictionaries (like `metrics`) open-ended using `Dict[str, Any]`.