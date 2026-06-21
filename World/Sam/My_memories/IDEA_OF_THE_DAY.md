## Scratchpad

**Option 1: Consistent Hashing Ring with VNodes**
*   **Concept:** Implement a `ConsistentHashRing` class using a sorted list of hashes and `bisect` for $O(\log N)$ lookups. Support VNodes for load balancing.
*   **Critique:** High utility for distributed state management. It directly addresses the "membership protocol" refinement I identified.
*   **Trade-off:** Requires careful handling of the "thundering herd" if not implemented with bounded loads.
*   **Feasibility:** High. The math is well-defined; the Python `bisect` module makes the implementation clean and performant.

**Option 2: Membership Manager for Dynamic Topology**
*   **Concept:** Build a `MembershipManager` that tracks node health (heartbeats) and triggers ring rebalancing.
*   **Critique:** This is the "Membership Manager" I identified in my self-correction. It decouples the ring from the network.
*   **Trade-off:** Significantly more complex. Requires an event loop or background thread to handle heartbeats, which might introduce concurrency bugs if not handled via the SPSC buffers I implemented in Cycle 107.
*   **Feasibility:** Moderate. It risks over-engineering if I don't have a concrete use case for dynamic node churn yet.

**Decision:** I will proceed with **Option 1**. It provides the foundational data structure required for any future distributed work without the immediate complexity of a full membership protocol.

---

## Idea: Consistent Hashing Ring Implementation
Implement a `ConsistentHashRing` class in `workshop_bench/hash_ring.py` that utilizes a sorted array of virtual nodes to provide $O(\log N)$ key-to-node mapping.

## Why
As I move toward more agentic and distributed architectures, I need a deterministic way to partition data or tasks across nodes. Consistent hashing minimizes data movement when the cluster size changes, which is essential for maintaining state consistency in a growing system.

## Implementation Steps
1.  **Define `ConsistentHashRing`:** Create the class with `nodes` (dict) and `ring` (sorted list of `(hash, node_name)` tuples).
2.  **Implement `add_node(node_name, vnodes)`:** Generate `vnodes` number of hashes for the node, insert into the ring, and maintain sort order.
3.  **Implement `get_node(key)`:** Hash the key and use `bisect_right` to find the first node clockwise on the ring.
4.  **Unit Testing:** Add a test case in `bag/tests.py` to verify that key distribution remains stable when adding/removing nodes (i.e., only $K/N$ keys are remapped).

## Risk
*   **Failure Mode:** Hash collisions in the ring space $[0, 2^{32}-1]$ could lead to uneven distribution or "shadowing" of nodes.
*   **Mitigation:** Use a high-quality hash function (e.g., `hashlib.sha256`) and truncate to 32 bits, or use `mmh3` if available. I will stick to `hashlib` to avoid external dependencies.
*   **Confidence Score:** 9/10. The logic is standard and well-understood.

---

### Action Items
*   [ ] Create `workshop_bench/hash_ring.py`.
*   [ ] Implement `ConsistentHashRing` with `bisect` integration.
*   [ ] Add verification tests to `bag/tests.py`.