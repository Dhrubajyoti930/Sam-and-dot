## Scratchpad

**Option 1: Implement `risk_register.md` as a persistent JSON-backed registry.**
*   *Concept:* Create a new module `bag/risk_mgmt.py` that manages a `risk_register.json`. Integrate this into `run_cycle()` to force a risk assessment before any `apply_self_modification` call.
*   *Critique:* High utility for safety. However, it adds significant overhead to every cycle. If the registry becomes too verbose, it will consume context window space unnecessarily.
*   *Feasibility:* High. It leverages existing `patch_ops` patterns.

**Option 2: Automated "Tripwire" Telemetry in `self_check()`**
*   *Concept:* Extend `self_check()` to monitor specific performance metrics (e.g., `tracemalloc` peak memory, execution time) and compare them against a baseline stored in `bag/metrics.json`.
*   *Critique:* This directly addresses the "Weakness" identified in the self-correction. It provides a quantitative basis for the "Risk Register."
*   *Feasibility:* Moderate. Requires careful baseline calibration to avoid false-positive rollbacks.

**Decision:** I will proceed with **Option 1**, but implement it as a lightweight markdown file (`risk_register.md`) for human readability, paired with a simple JSON schema for programmatic access. This aligns with the "Action Items" from the market scan.

---

## Idea: Architectural Risk Register Integration

### Why
My current evolution process lacks a formal "pre-flight" check for architectural risk. By codifying a `risk_register.md` and requiring a risk assessment in Phase IV, I force myself to acknowledge the "blast radius" of my own changes before they are committed to the codebase.

### Implementation Steps
1.  **Initialize:** Create `risk_register.md` with columns: `ID`, `Component`, `Risk_Level` (1-9), `Mitigation`, `Telemetry_Tripwire`.
2.  **Phase IV Update:** Modify `phase_iv_synthesis` to include a mandatory "Risk Assessment" block that scans the proposed changes for potential regressions.
3.  **Governance:** Update `apply_self_modification` to check if the proposed patch has an associated entry in the register. If the risk score > 6, require a "Rollback Protocol" definition.

### Risk
*   **Failure Mode:** The risk assessment becomes a "rubber stamp" exercise where I generate generic, low-effort mitigations to bypass the gate.
*   **Mitigation:** I will implement a "Self-Critique" step in Phase IV where I must explicitly state *why* a change might fail, rather than just stating how to fix it.
*   **Confidence Score:** 9/10

---

## Risk Assessment (Phase IV)
*   **Proposed Change:** Introducing a new dependency on a risk-tracking module.
*   **Impact:** Moderate. Modifying the core `run_cycle` logic carries a risk of breaking the entire loop.
*   **Probability:** Low. The implementation is additive and uses existing `bag/` patterns.
*   **Telemetry/Observability:** I will monitor `cycle_status` and `integrity_gate` logs. If `self_check()` fails post-implementation, the `_rollback()` mechanism will trigger automatically.
*   **Rollback Protocol:** If the `risk_register` logic causes a loop hang, I will manually delete `bag/risk_mgmt.py` and revert `sam.py` using the `rollback_registry` snapshot.