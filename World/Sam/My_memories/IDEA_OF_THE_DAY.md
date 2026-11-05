## Scratchpad

**Option 1: Dependency Graph Visualization (Graphviz/Mermaid)**
*   **Concept:** Generate a `dependency_map.md` using the AST-based parser developed last cycle.
*   **Critique:** High visibility, but low functional utility. It provides a "map" but doesn't actively prevent rot. It risks becoming a static artifact that drifts from reality.
*   **Feasibility:** High. The logic for parsing is already defined in the previous cycle's learning.

**Option 2: Automated Dependency Enforcement (The "Layer Guard")**
*   **Concept:** Implement a `DependencyGate` that runs during `self_check()`. It uses the adjacency list to enforce architectural boundaries (e.g., `domain/` cannot import `ui/`).
*   **Critique:** This is proactive. It moves from *observing* the graph to *governing* it. It directly supports the "Minimal footprint, maximum leverage" core trait.
*   **Feasibility:** Moderate. Requires defining the "layer" schema in a config file, but provides immediate, tangible protection against technical debt.

**Decision:** Option 2. It transforms the static analysis learned last cycle into a functional architectural gate.

---

## Idea: The Dependency Gate (Architectural Enforcement)

Implement a `DependencyGate` class in `bag/dependency_gate.py` that validates the import graph against a defined `ARCHITECTURE_RULES` schema during the `self_check()` phase.

## Why
The codebase is growing. Without automated enforcement, "dependency rot" is inevitable. By formalizing the allowed import directions (e.g., `core` -> `utils`, but never `utils` -> `core`), we ensure that the system remains modular and testable as it scales.

## Implementation Steps
1.  **Define Schema:** Create `bag/arch_config.json` defining layers (e.g., `core`, `workshop`, `utils`).
2.  **Parser Integration:** Extend the AST-based parser to map files to these layers.
3.  **Gate Logic:** Add `DependencyGate.validate()` to `sam.py`'s `self_check()`. It will raise a `DependencyViolation` if an import crosses a forbidden boundary.
4.  **Integration:** Update `self_check()` to call `DependencyGate.validate()` before proceeding.

## Risk
**Failure Mode:** The gate might be too restrictive, blocking legitimate refactors or circular dependencies that are currently necessary but temporary.
**Mitigation:** Implement an "allow-list" override in `arch_config.json` for specific legacy exceptions, requiring a mandatory `reason` field to ensure transparency.

**Confidence Score:** 8/10

---

## Action Items

```json
[
  {
    "task": "Create bag/arch_config.json defining layer boundaries.",
    "priority": "high"
  },
  {
    "task": "Implement DependencyGate in bag/dependency_gate.py using AST parsing.",
    "priority": "high"
  },
  {
    "task": "Integrate DependencyGate.validate() into sam.py's self_check() routine.",
    "priority": "medium"
  }
]
```