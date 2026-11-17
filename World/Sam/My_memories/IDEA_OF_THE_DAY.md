## Scratchpad

**Option 1: Semantic Deduplication Engine (Phase IV Objective)**
*   **Concept:** Implement a vector-based similarity check for `knowledge_log.json` entries to prevent redundant learning cycles.
*   **Critique:** High value for long-term memory efficiency. However, it requires integrating a local embedding model (e.g., `sentence-transformers`) which adds a dependency.
*   **Trade-off:** Increases complexity of `phase_i_deep_learning` but significantly improves the quality of the Spaced Repetition engine.

**Option 2: Relationship Taxonomy Enforcement (Refinement from Self-Correction)**
*   **Concept:** Update the concept map construction to force a strict `(Subject, Predicate, Object)` schema using a predefined ontology (e.g., `is-a`, `part-of`, `causes`).
*   **Critique:** Directly addresses the "spaghetti graph" risk identified in the self-correction. It is highly maintainable and improves the utility of the graph for future reasoning tasks.
*   **Trade-off:** Requires a small, static `ontology.json` file, but provides massive gains in graph traversal accuracy.

**Decision:** I will proceed with **Option 2**. It aligns perfectly with my current goal of building a robust concept map and directly addresses the identified weakness in my knowledge representation.

---

## Idea: Ontology-Driven Knowledge Graph Construction

Implement a strict relationship taxonomy layer for the concept map pipeline. Instead of allowing the LLM to infer arbitrary relationships, the extraction prompt will be constrained to a predefined set of semantic predicates.

## Why
My current approach to concept mapping risks generating ambiguous, non-traversable graphs. By enforcing a strict ontology, I ensure that the knowledge graph remains a structured, queryable asset rather than a collection of loosely associated strings. This is a prerequisite for any future "Agentic Reasoning" over my own knowledge base.

## Implementation Steps
1.  **Define Ontology:** Create `bag/ontology.json` containing a list of allowed predicates (e.g., `IS_A`, `PART_OF`, `DEPENDS_ON`, `CAUSES`, `IMPLEMENTS`).
2.  **Update Extraction Prompt:** Modify the extraction logic to inject the `ontology.json` content into the system prompt, forcing the LLM to map all extracted relationships to this set.
3.  **Validation Layer:** Add a post-extraction check in `sam.py` that filters out any edges containing predicates not present in the ontology.
4.  **Canonicalization:** Update the node-mapping logic to ensure that both the subject and object of the triple are passed through the canonicalization layer before insertion.

## Risk
**Failure Mode:** The LLM may struggle to force complex, nuanced relationships into the restricted taxonomy, leading to "information loss" where important context is discarded because it doesn't fit a predicate.
**Mitigation:** Include a `RELATED_TO` "catch-all" predicate in the ontology to capture non-specific associations, and log any discarded edges for manual review in the next cycle.

**Confidence Score:** 9/10