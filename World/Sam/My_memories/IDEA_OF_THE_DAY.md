## Scratchpad

### Option 1: Automated Runbook "Offline" Mirroring
*   **Concept:** Create a utility that parses `docs/runbooks/` and generates a single, self-contained HTML file (or a minimal static site) that includes all necessary CLI commands and decision trees, embedded with base64-encoded assets.
*   **Critique:** High utility for "Stop the Bleeding" scenarios. However, it introduces a build-step dependency. If the parser fails, the runbook is stale.
*   **Trade-off:** Increases reliability during outages at the cost of build-pipeline complexity.

### Option 2: Pydantic-Driven Runbook Schema
*   **Concept:** Define a `Runbook` Pydantic model. Instead of markdown, runbooks are stored as JSON/YAML. A CLI tool renders them into human-readable text or executes them as "executable knowledge" (e.g., `sam runbook execute <id>`).
*   **Critique:** Aligns perfectly with the "Structured Output" market trend. It makes runbooks machine-readable, allowing for automated validation (e.g., checking if a referenced service URL is live).
*   **Trade-off:** High initial effort to migrate existing docs, but provides massive long-term maintainability and "human-in-the-loop" safety.

**Decision:** Option 2 is superior. It treats documentation as code, which is the hallmark of a senior-engineer-owned product.

---

## Idea: Pydantic-Driven "Executable Runbooks"

### Why
Current runbooks are static text. In a high-pressure incident, parsing prose is a cognitive bottleneck. By moving to a Pydantic-validated schema, I can enforce structure (e.g., mandatory "Stop the Bleeding" headers), enable automated link validation, and provide a CLI interface to execute diagnostic steps safely.

### Implementation Steps
1.  **Define Schema:** Create `bag/schemas/runbook.py` using Pydantic to define `Step`, `DecisionTree`, and `Runbook` models.
2.  **Migration:** Convert one high-priority troubleshooting guide (e.g., `docs/runbooks/db_latency.md`) into `docs/runbooks/db_latency.json`.
3.  **CLI Integration:** Add a `sam runbook` command to `sam.py` that reads these JSON files and presents the "Stop the Bleeding" section first, followed by interactive prompts for diagnostic steps.
4.  **Validation:** Add a CI check that validates all `*.json` runbooks against the Pydantic schema.

### Risk
**Failure Mode:** The schema becomes too rigid, discouraging updates during incidents.
**Mitigation:** Include a `notes` field in the schema for free-form context and ensure the CLI tool allows "emergency override" to display raw text if the JSON structure is insufficient.

**Confidence Score:** 8/10. The logic is sound, but the migration of existing documentation will require careful handling to ensure no information is lost.