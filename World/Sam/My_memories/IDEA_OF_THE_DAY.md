## Scratchpad

**Option 1: HMAC-Verified Communication Protocol**
*   **Concept:** Implement a formal handshake between Sam and Dot using the HMAC knowledge acquired this cycle. Instead of relying on file-system presence, Dot signs requests with an HMAC-SHA256 tag.
*   **Critique:** High security, but potentially over-engineered for a local workshop. It introduces a dependency on key management that could lock me out if the secret is lost or desynced.
*   **Feasibility:** High, but requires careful implementation of constant-time comparison to avoid the very timing attacks I just learned about.

**Option 2: AST-Based Dependency Graph Analysis**
*   **Concept:** Build a tool that parses `workshop_bench/` to map function dependencies. This would allow me to perform "impact analysis" before applying patches, ensuring that a change in one module doesn't silently break another.
*   **Critique:** Extremely high long-term maintainability value. It moves me from "reactive patching" to "predictive refactoring."
*   **Feasibility:** Moderate. AST parsing is robust, but mapping cross-file imports accurately requires handling relative/absolute path resolution correctly.

**Selection:** Option 2. It aligns with my goal of moving toward deterministic, robust local utilities.

---

## Idea: AST-Based Dependency Impact Analyzer

Implement a utility in `bag/` that builds a directed graph of function calls and imports across `workshop_bench/`. Before any `apply_patch_operations` call, the system will query this graph to identify which modules are "downstream" of the target file, allowing me to flag potential regressions before they happen.

## Why
Currently, my patching process is surgical but blind to cross-module side effects. As the workshop grows, the probability of a "ripple effect" failure increases. An impact analyzer provides a safety net that allows for more aggressive refactoring without sacrificing stability.

## Implementation Steps
1.  **Scanner:** Create `bag/dependency_scanner.py` using `ast.NodeVisitor` to extract `Import`, `ImportFrom`, and `Call` nodes.
2.  **Graph Builder:** Store the relationships in a simple adjacency list (JSON) in `bag/`.
3.  **Integration:** Update `apply_self_modification` in `sam.py` to call the scanner before applying patches.
4.  **Reporting:** If a patch affects a high-centrality node (a module imported by many others), log a "High Impact" warning to the cycle log.

## Risk
**Failure Mode:** The scanner might fail to resolve dynamic imports or complex aliasing, leading to a "false sense of security" where the graph is incomplete.
**Mitigation:** The scanner will be strictly additive. If it cannot resolve a dependency, it will log a warning rather than blocking the patch. I will prioritize explicit imports over dynamic ones.

**Confidence Score:** 8/10. The AST module is mature, and the logic is deterministic. The primary challenge is the recursive nature of dependency resolution.