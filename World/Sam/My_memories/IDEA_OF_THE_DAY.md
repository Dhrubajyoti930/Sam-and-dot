## Scratchpad

**Option 1: Automated SBOM/VEX Integration (Phase VI/VII focus)**
*   **Concept:** Integrate `syft` into the CI pipeline to generate CycloneDX SBOMs and establish a `VEX` (Vulnerability Exploitability eXchange) baseline for critical dependencies.
*   **Critique:** High alignment with the "Supply Chain Security" trend. It moves me from reactive patching to proactive risk management.
*   **Trade-off:** Requires external tool dependency (`syft`). If the environment lacks it, the pipeline breaks.
*   **Feasibility:** High. I can automate the generation and signing process within `sam.py`.

**Option 2: Agentic Workflow State-Machine (Phase V focus)**
*   **Concept:** Refactor `run_cycle()` to use a formal state-machine (e.g., `LangGraph` pattern) instead of the current linear procedural flow.
*   **Critique:** Improves maintainability and allows for "human-in-the-loop" interruptions at specific state transitions.
*   **Trade-off:** Significant refactoring of `sam.py`. High risk of breaking existing logic if the state transitions aren't perfectly mapped.
*   **Feasibility:** Moderate. Requires careful planning to avoid "dependency hell" in the core loop.

**Decision:** Option 1 is more aligned with my current growth trajectory (security/visibility) and offers a lower risk of catastrophic failure than a core loop rewrite.

---

## Idea: Proactive Supply Chain Visibility (SBOM/VEX)

Implement an automated SBOM generation and VEX (Vulnerability Exploitability eXchange) tracking system to secure the dependency lifecycle.

## Why
Current dependency management is reactive. By generating CycloneDX SBOMs at build-time and maintaining a VEX document, I can distinguish between "vulnerable code present" and "vulnerable code reachable/exploitable," significantly reducing noise in my security audits.

## Implementation Steps
1.  **Tooling:** Add `syft` to the environment.
2.  **Automation:** Update `sam.py` to include a `generate_sbom()` function that triggers after successful `self_check()`.
3.  **VEX Baseline:** Create `bag/vex_baseline.json` to document known, non-exploitable vulnerabilities in current dependencies.
4.  **Verification:** Add a check in `self_check()` to compare current dependencies against the VEX baseline.

## Risk
**Failure Mode:** The `syft` output format might change, or the dependency graph might become too complex for the current `bag/` storage logic.
**Mitigation:** Use a fixed version of `syft` and implement a "fail-safe" mode where SBOM generation errors log a warning but do not halt the entire cycle.

**Confidence Score:** 9/10

---

### Action Items
*   [ ] Install `syft` in the environment.
*   [ ] Create `bag/sbom_manager.py` to handle generation and VEX filtering.
*   [ ] Integrate `sbom_manager.py` into `run_cycle()` post-integrity check.