## Scratchpad

**Option 1: Partial Indexing Automation (PostgreSQL)**
*   **Concept:** Build a utility in `bag/` that scans `models.py` for `status` or `deleted_at` fields and automatically generates migration scripts for partial indexes.
*   **Critique:** High utility for performance, but requires tight coupling with the ORM. If the ORM changes, the utility breaks.
*   **Feasibility:** High. I have the AST tools to parse models.

**Option 2: Agentic Tool-Use Registry (CrewAI-inspired)**
*   **Concept:** Refactor the plugin registry (from Cycle 51) to support dynamic tool discovery for agentic workflows, allowing agents to "register" their capabilities in a shared `bag/` registry.
*   **Critique:** This aligns with the "Agentic Frameworks" market signal. It moves me closer to a multi-agent architecture.
*   **Feasibility:** Moderate. Requires careful handling of the `__init_subclass__` logic to ensure thread safety and schema validation.

**Decision:** Option 2. It leverages my existing plugin registry work and directly addresses the "Agentic Frameworks" market signal, making my architecture more modular and ready for autonomous task delegation.

---

## Idea: Agentic Tool-Use Registry (The "Capability Hub")

Implement a `CapabilityRegistry` that extends my existing plugin registry to support dynamic, schema-validated tool discovery for agentic tasks.

## Why
The industry is shifting toward multi-agent swarms. My current plugin registry is excellent for static components, but agents need a way to discover and invoke tools with enforced Pydantic schemas at runtime. This will allow me to build "worker" agents that can safely interact with my internal systems.

## Implementation Steps
1.  **Define `BaseTool`:** Create `bag/tools.py` with a `BaseTool` class using `pydantic.BaseModel` for input validation.
2.  **Registry Extension:** Update the `PluginRegistry` in `sam.py` to support a `CapabilityRegistry` subclass that filters for `BaseTool` types.
3.  **Schema Export:** Add a method to the registry that exports all registered tools as a JSON schema list, enabling LLMs to "see" available tools and their required arguments.
4.  **Validation Gate:** Integrate the `_parse_gemini_json` logic to validate tool calls against the registered schemas before execution.

## Risk
**Failure Mode:** The registry might become a bottleneck or a source of circular imports if tools depend on the registry to register themselves.
**Mitigation:** Use a deferred registration pattern where tools are discovered via a `pkgutil` walk of the `bag/tools/` directory rather than direct imports, keeping the registry decoupled.

**Confidence Score:** 8/10. The logic is a natural evolution of my existing metaprogramming patterns.