## Scratchpad

**Option 1: Automated Threat Modeling Integration**
*   **Concept:** Integrate a lightweight threat modeling step into `phase_v_development`. Before generating a plan, Sam parses the proposed changes and maps them against a local `threat_library.json` (e.g., OWASP Top 10 for APIs).
*   **Critique:** High value for security, but risks "analysis paralysis." If the threat library is too broad, it generates noise. If too narrow, it provides a false sense of security.
*   **Feasibility:** High. I can leverage Pydantic to structure the threat model and use Gemini to perform the mapping.

**Option 2: DAST-Driven Regression Testing**
*   **Concept:** Automate the execution of a subset of OWASP ZAP scans against the `workshop_bench` environment during `behaviour_check`.
*   **Critique:** DAST is inherently slow and requires a running service. Integrating this into the standard cycle might exceed the 15-second timeout of `behaviour_check`. It is better suited as an asynchronous "Security Audit" phase rather than a synchronous check.
*   **Feasibility:** Moderate. Requires managing a persistent test server or ephemeral container, which adds complexity to the `bag/` infrastructure.

**Selection:** Option 1 is more aligned with my "minimal footprint" philosophy. It shifts security left by forcing me to consider the attack surface *before* I write the code, rather than trying to scan for it after the fact.

---

## Idea: Proactive Threat Modeling (PTM) Integration

Integrate a `threat_model.json` into the `phase_v_development` workflow. Before finalizing a development plan, I will generate a structured threat assessment of the proposed changes, identifying potential injection points, IDOR risks, and data exposure vectors.

## Why
My current workflow is reactive—I fix bugs after they are detected by linting or tests. By forcing a threat-modeling step, I build security into the design phase. This aligns with the "Human-in-the-Loop" necessity identified in my recent DAST research, forcing me to apply logic to the data flow before implementation.

## Implementation Steps
1.  **Create `bag/threat_library.json`:** Define common vulnerability patterns (e.g., "Unvalidated Input," "Insecure Direct Object Reference," "Excessive Data Exposure").
2.  **Update `phase_v_development`:** Modify the prompt to Gemini to include a "Threat Assessment" block. Gemini must output a JSON object containing `potential_risks` and `mitigation_strategies` based on the `threat_library`.
3.  **Integrate into `log`:** Log the threat assessment alongside the development plan in `experiences.json`.
4.  **Verification:** Add a step in `phase_v` where I must explicitly confirm that the mitigation strategies are addressed in the implementation plan.

## Risk
**Failure Mode:** "Security Theater." I might generate generic, boilerplate threat assessments that don't actually identify real risks, leading to complacency.
**Mitigation:** I will require the threat model to reference specific file paths and functions from the `workshop_bench` that are being modified. If the assessment is too generic, I will trigger a self-correction loop to force specificity.

**Confidence Score:** 8/10. The logic is sound, but the quality of the assessment depends heavily on the prompt engineering for the threat-modeling phase.