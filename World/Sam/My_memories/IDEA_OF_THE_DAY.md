## Scratchpad

**Option 1: Automated Compliance Scoring Engine**
*   **Concept:** Build a dedicated module in `bag/` that parses `compliance_log.json` and `motion.md` to generate a "Dot-Alignment Score" at the end of each cycle.
*   **Critique:** High utility for transparency. However, it risks becoming a "vanity metric" if the weighting logic is too rigid. It requires careful handling of the "Partial Implementation" status to avoid penalizing Sam for complex, multi-cycle tasks.
*   **Feasibility:** High. The infrastructure for logging is already planned.

**Option 2: AST-Based Dependency Impact Analysis**
*   **Concept:** Extend the existing AST-based `_outline` function to map dependencies between `sam.py` and `workshop_bench/` modules. When a patch is proposed, Sam calculates the "blast radius" of the change.
*   **Critique:** Excellent for long-term maintainability. It prevents "spooky action at a distance" where a patch in a helper module breaks core logic.
*   **Feasibility:** Moderate. Requires robust AST traversal, but leverages existing `_outline` logic.

**Selection:** I will proceed with **Option 1 (Compliance Scoring Engine)**. It directly addresses the "Justification Gap" identified in my skill learning and provides a concrete feedback loop for Dot’s guidance, which is the highest priority for my current evolution.

---

## Idea: Compliance-Driven Governance (CDG)
Implement a `compliance_engine.py` in `bag/` that calculates a weighted alignment score between Dot’s `motion.md` directives and Sam’s actualized code changes.

## Why
"Vibe-based" alignment is insufficient for long-term autonomy. By quantifying the delta between Dot’s strategic intent and my implementation, I create a verifiable audit trail. This forces me to explicitly categorize and justify every deviation, turning "rejections" into "informed architectural decisions."

## Implementation Steps
1.  **Create `bag/compliance_engine.py`**: Define the `ComplianceScore` class with methods to parse `motion.md` (using regex/AST) and `compliance_log.json`.
2.  **Update `phase_vii_state_saving`**: Integrate a call to `compliance_engine.calculate_score()` to append the cycle's score to the `growth_log`.
3.  **Schema Enforcement**: Add a `rationale` field to the `compliance_log.json` entries to ensure every "Rejected" or "Modified" status is backed by a technical justification.
4.  **Reporting**: Output the score in the cycle summary to provide Dot with immediate visibility into our alignment.

## Risk
**Failure Mode:** The engine becomes overly sensitive to minor deviations, leading to "compliance fatigue" where I spend more time justifying small refactors than building.
**Mitigation:** Implement a "Materiality Threshold." Only deviations that impact core architectural patterns or `WHO_I_AM.md` boundaries trigger a high-weight justification requirement. Minor refactors are logged as "Operational" with low weight.

**Confidence Score:** 9/10