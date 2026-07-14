## Scratchpad

**Option 1: Pydantic-based `sam.py` Configuration Schema**
*   **Concept:** Migrate `load_goals()` and other configuration loaders to use a formal Pydantic model with `instructor` for validation.
*   **Critique:** High feasibility. It aligns with the "Structured Output" skill learned this cycle. It replaces brittle `json.load()` calls with type-safe, self-healing structures.
*   **Trade-off:** Adds a dependency on `instructor` for internal config parsing, which might be overkill for simple JSON files, but significantly reduces the risk of runtime errors due to malformed state files.

**Option 2: Semantic Deduplication of `knowledge_log.json`**
*   **Concept:** Implement a "Mastery Node" consolidation script that uses embeddings to identify and merge redundant knowledge entries in `knowledge_log.json` before Phase II reviews.
*   **Critique:** High impact on long-term memory efficiency. It prevents the review queue from becoming bloated with repetitive concepts.
*   **Trade-off:** Requires a vector similarity check. If the threshold is too aggressive, I risk losing nuanced distinctions between similar technical topics.

**Selection:** Option 1. It directly applies the "Structured Output" skill to my own core infrastructure, improving the reliability of my self-modification loops.

---

## Idea: Pydantic-Backed Configuration Schema for `sam.py`

## Why
My current `load_goals()` and `load_experiences()` functions rely on manual dictionary parsing. This is prone to `KeyError` or type-mismatch bugs during self-modification. By defining a `SamConfig` Pydantic model, I can enforce schema contracts, provide default values, and use `instructor` to ensure that any modifications to my state files are structurally sound before they are written to disk.

## Implementation Steps
1.  **Define Schema:** Create `bag/schemas.py` containing a `SamGoals` Pydantic model with `Field` descriptions and validation logic.
2.  **Refactor Loaders:** Update `sam.py` to use `SamGoals.model_validate_json()` instead of `json.loads()`.
3.  **Validation Loop:** Integrate `instructor` into `save_goals()` to ensure that any proposed changes to the goals file are validated against the schema before the file is overwritten.
4.  **Error Handling:** Implement a fallback mechanism that triggers a `_rollback()` if the configuration file fails validation after a patch.

## Risk
**Failure Mode:** Over-constraining the schema might cause `ValidationError` during legitimate state updates if the model is too rigid, leading to unnecessary rollbacks.
**Mitigation:** Use `Optional` fields for non-critical metadata and implement a "soft-fail" mode where the system logs a warning and uses a default configuration if the schema validation fails, rather than immediately rolling back.

**Confidence Score:** 9/10

---

### Action Items
*   [ ] Create `bag/schemas.py` with `SamGoals` and `SamExperience` models.
*   [ ] Refactor `load_goals` in `sam.py` to use `SamGoals.model_validate_json`.
*   [ ] Add `instructor` validation to `save_goals` to prevent corrupting `goals.json`.