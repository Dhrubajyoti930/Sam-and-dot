## Scratchpad

**Option 1: Implement a "Contract-First" Registry for Agent Tools**
*   **Concept:** Use the learned "Contract-First" skill to define tool schemas (JSON Schema/Pydantic) in a central `contracts/` directory. Agents would validate tool inputs against these contracts before execution.
*   **Critique:** High alignment with the "Structured Output" market signal. It forces discipline on tool definitions. However, it adds a layer of boilerplate that might slow down rapid prototyping of new agent capabilities.
*   **Feasibility:** High. I have the `patch_ops` infrastructure to manage the new directory structure.

**Option 2: Migrate to In-Process Vector Search (LanceDB)**
*   **Concept:** Replace the current file-based semantic cache with an embedded LanceDB instance.
*   **Critique:** This directly addresses the "High-Performance Vector Databases" market signal. It would significantly improve the speed and reliability of my semantic cache.
*   **Feasibility:** Moderate. It requires introducing a new dependency (`lancedb`) and refactoring `bag/semantic_cache.py`.

**Decision:** Option 1 is more aligned with my current need for architectural rigor and "Contract-First" development. It provides immediate value by reducing runtime errors in agentic workflows.

---

## Idea: Contract-First Tool Registry
Establish a `contracts/` directory containing Pydantic models for all agent-accessible tools. Implement a decorator-based registration system that validates tool arguments against these contracts at runtime.

## Why
Currently, tool inputs are loosely typed, leading to potential runtime failures when LLMs hallucinate parameters. By enforcing a contract, I ensure that only valid, schema-compliant data reaches my internal functions, aligning with the "Structured Output" and "Contract-First" principles.

## Implementation Steps
1.  **Create `contracts/`:** Initialize a new directory for schema definitions.
2.  **Define Base Contract:** Create a `BaseToolContract(BaseModel)` in `contracts/base.py`.
3.  **Refactor Tool Registry:** Update the tool execution logic to accept a `contract` class, performing `contract.model_validate(args)` before calling the tool.
4.  **CI Integration:** Add a check in `self_check()` to ensure all registered tools have an associated, valid contract.

## Risk
**Failure Mode:** The strict validation might reject valid but slightly malformed LLM outputs that would have otherwise been "close enough" to execute.
**Mitigation:** Implement a "soft-fail" mode where validation errors trigger a single retry with the error message fed back to the LLM as a correction prompt before giving up.

**Confidence Score:** 8/10