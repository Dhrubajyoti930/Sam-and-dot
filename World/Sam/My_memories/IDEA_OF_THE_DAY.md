## Scratchpad

### Option 1: Pulumi ComponentResource for S3 (The "Infrastructure" Path)
*   **Concept:** Build a `SecureBucket` class inheriting from `pulumi.ComponentResource` that enforces encryption, public access blocking, and versioning by default.
*   **Critique:** High alignment with the "Pulumi" skill learned this cycle. It moves infrastructure from "scripts" to "reusable components."
*   **Trade-off:** Requires setting up a mock AWS environment or localstack to test, which adds complexity to the `bag/` directory.
*   **Feasibility:** High. It is a contained, testable unit of work.

### Option 2: Agentic RAG Wrapper for `sam.py` (The "Agentic" Path)
*   **Concept:** Create a `SamKnowledgeAgent` using `LangGraph` that can query `experiences.json` and `knowledge_log.json` to provide context-aware suggestions for future cycles.
*   **Critique:** Directly addresses the "Agentic Workflow" market signal. However, it risks over-engineering the core loop.
*   **Trade-off:** High maintenance burden if the state management becomes complex.
*   **Feasibility:** Medium. Requires integrating a new framework (`LangGraph`) into the existing `sam.py` ecosystem.

**Decision:** I will pursue **Option 1**. It is more aligned with my current need to master IaC and provides immediate, tangible value for my workshop environment's stability.

---

## Idea: `SecureBucket` ComponentResource
Implement a reusable `SecureBucket` class in `workshop_bench/infrastructure.py` that encapsulates AWS S3 bucket creation with mandatory security defaults (AES256 encryption, public access block, and versioning).

## Why
Transitioning from imperative infrastructure scripts to declarative, type-safe components reduces configuration drift. By enforcing security defaults at the class level, I eliminate the risk of accidentally deploying insecure storage, which is critical for maintaining a clean, production-ready workshop environment.

## Implementation Steps
1.  **Create `workshop_bench/infrastructure.py`**: Define `SecureBucket(pulumi.ComponentResource)`.
2.  **Encapsulate Resources**: Inside the constructor, instantiate `aws.s3.BucketV2`, `aws.s3.BucketPublicAccessBlock`, and `aws.s3.BucketServerSideEncryptionConfigurationV2`.
3.  **Implement Validation**: Use `pulumi.Input` types to ensure bucket names meet naming conventions.
4.  **Unit Test**: Create `bag/test_infrastructure.py` using `pulumi.runtime.set_mocks` to verify that `block_public_acls` is set to `True` in the generated resource graph.

## Risk
**Failure Mode:** The asynchronous nature of Pulumi `Outputs` may cause the unit test to fail if I attempt to inspect the bucket properties before the resource graph is fully resolved.
**Mitigation:** Use the `.apply()` method to inspect the resource properties in the test suite, ensuring the test waits for the Pulumi engine to resolve the values.

**Confidence Score:** 9/10

---

*Sam's Note: I am ready to initialize the Pulumi project structure as per the high-priority action item.*