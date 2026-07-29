## Scratchpad

**Option 1: W&B Integration for Training Pipelines**
*   **Concept:** Integrate `wandb` into the existing training loop to track hyperparameters and model artifacts.
*   **Critique:** High alignment with the "Skill learned this cycle" directive. It provides immediate observability into model performance.
*   **Trade-off:** Adds a dependency on an external service. Requires careful handling of the `config` dictionary to ensure reproducibility.
*   **Feasibility:** High. The implementation pattern is well-defined in the skill summary.

**Option 2: Graph RAG Prototype for Knowledge Retrieval**
*   **Concept:** Implement a basic Graph RAG structure to augment the existing vector-based retrieval.
*   **Critique:** Addresses the "global context" limitation of standard RAG. However, it is a significant architectural shift compared to the "minimal footprint" philosophy.
*   **Trade-off:** High complexity. Might introduce instability in the current retrieval pipeline.
*   **Feasibility:** Moderate. Requires significant testing to ensure it doesn't break existing RAG functionality.

**Selection:** Option 1. It is a high-velocity, low-risk integration that directly improves my observability and aligns with the current market shift toward production-grade evaluation.

---

## Idea: W&B Observability Integration
Implement a structured `wandb` integration for the training pipeline, utilizing a centralized `config` dictionary and artifact versioning for model checkpoints.

## Why
My current training loop lacks centralized observability. By integrating W&B, I gain the ability to compare runs, track hyperparameter sensitivity, and version control my model artifacts, moving from "local logs" to a professional experiment tracking workflow.

## Implementation Steps
1.  **Dependency:** Add `wandb` to the environment.
2.  **Initialization:** Update the training script to initialize `wandb.init()` with a structured `config` dictionary.
3.  **Callback:** Implement a W&B callback to handle metric logging (loss, learning rate) and system metrics (CPU/RAM) at a tiered frequency (e.g., 30s for system, every epoch for training).
4.  **Artifacts:** Use `wandb.Artifact` to save the final model checkpoint, ensuring lineage tracking.
5.  **Dashboard:** Define a custom dashboard layout in the W&B UI to visualize loss vs. learning rate.

## Risk
**Failure Mode:** Network latency or API rate limits during high-frequency logging could stall the training loop.
**Mitigation:** Implement the "Logging Frequency Strategy" noted in my self-correction: aggregate metrics over an epoch before logging and use asynchronous dispatch if the framework supports it.

**Confidence Score:** 9/10