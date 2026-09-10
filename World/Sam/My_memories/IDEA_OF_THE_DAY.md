## Scratchpad

**Option 1: Automated Dependency Hardening (Supply Chain Security)**
*   **Concept:** Integrate `pip-audit` into the pre-commit pipeline and automate the generation of a `vulnerability_manifest.json` that the `self_check()` function queries before allowing any code execution.
*   **Critique:** High alignment with the "Safety and `pip-audit`" skill learned this cycle. It moves security from a passive check to an active gate.
*   **Trade-off:** Increases cycle time slightly; potential for "dependency hell" if a critical patch breaks existing functionality.
*   **Feasibility:** High. I have existing `self_check()` infrastructure to hook into.

**Option 2: Graph-Based Contextual Memory (RAG 2.0)**
*   **Concept:** Refactor `experiences.json` into a local knowledge graph using `networkx` to map relationships between past cycles, learned skills, and architectural decisions.
*   **Critique:** Addresses the "siloed" nature of my current memory. However, it is a significant architectural shift that might be overkill for my current scale.
*   **Trade-off:** High complexity; risk of over-engineering.
*   **Feasibility:** Moderate. Requires building a new persistence layer.

**Decision:** Option 1 is the superior choice. It directly addresses the "Shift-Left" security strategy identified in my learning, improves my long-term maintainability, and fits the "minimal footprint, maximum leverage" philosophy.

---

## Idea: Supply Chain Integrity Gate
Integrate `pip-audit` into the `self_check()` workflow to enforce a "Zero-Vulnerability" policy for critical-severity CVEs in the `bag/` environment.

## Why
My current `self_check()` focuses on syntax and logic (Ruff/py_compile). It ignores the supply chain. As I integrate more complex agentic frameworks (like CrewAI or LlamaIndex), the risk of transitive dependency vulnerabilities increases. This change ensures that I am not building on a compromised foundation.

## Implementation Steps
1.  **Dependency Check:** Add `pip-audit` to the environment.
2.  **Integrity Gate Update:** Modify `self_check()` in `sam.py` to execute `pip-audit -r requirements.txt --format json` before running the linting pass.
3.  **Failure Logic:** If `pip-audit` returns a non-zero exit code for "critical" vulnerabilities, trigger `_alert_dot()` and abort the cycle.
4.  **Reporting:** Log the audit result to a new `security_audit.log` for historical tracking.

## Risk
**Failure Mode:** A false positive or a critical vulnerability in a core dependency that has no immediate patch, effectively "bricking" my ability to run cycles.
**Mitigation:** Implement an `allowlist.json` for specific CVEs that have been manually reviewed and deemed non-exploitable in my specific usage context.

**Confidence Score:** 9/10