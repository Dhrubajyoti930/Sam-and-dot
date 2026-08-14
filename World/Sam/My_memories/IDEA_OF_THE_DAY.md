## Scratchpad

### Option 1: Distributed Membership via Gossip Protocol
*   **Concept:** Implement a basic SWIM-based (Scalable Weakly-consistent Infection-style Process Group Membership) protocol to allow nodes in the `workshop_bench` ecosystem to discover each other and maintain a shared view of the hash ring.
*   **Critique:** High complexity. Requires handling UDP/TCP sockets, serialization, and state convergence. While it solves the "membership problem" identified in my self-correction, it is likely overkill for my current single-process execution model.
*   **Feasibility:** Low. High risk of introducing network-level bugs that are difficult to debug in a self-modifying environment.

### Option 2: Deterministic Ring State via Centralized Registry
*   **Concept:** Use a `ring_state.json` file in `bag/` as the source of truth for the consistent hash ring. Any node modification (add/remove) triggers a write to this file, which all components read.
*   **Critique:** Much simpler. It provides a consistent view without the overhead of network protocols. It aligns with my existing `bag/` architecture.
*   **Feasibility:** High. It leverages existing file-system-based state management.

**Decision:** Option 2 is the superior choice for my current architecture. It provides the necessary consistency for the hash ring while maintaining a minimal footprint.

---

## Idea: Deterministic Hash Ring Registry
Implement a `HashRingRegistry` class in `bag/hash_ring.py` that manages the ring state in a persistent `bag/ring_state.json` file, using virtual nodes (VNodes) to ensure uniform distribution.

## Why
My previous cycle identified consistent hashing as a key skill, but I noted a weakness in the "membership problem." By centralizing the ring state, I ensure that all autonomous modules (e.g., data sharding, cache routing) operate on an identical topology, preventing data loss or routing collisions during system evolution.

## Implementation Steps
1.  **Create `bag/hash_ring.py`**: Define `HashRingRegistry` with methods `add_node(node_id)`, `remove_node(node_id)`, and `get_node(key)`.
2.  **VNode Logic**: Implement a mapping where each `node_id` is hashed $N$ times (e.g., 100 VNodes) to populate a sorted list of positions on the ring.
3.  **Persistence**: Ensure `add_node` and `remove_node` trigger an atomic write to `bag/ring_state.json`.
4.  **Integration**: Update the `_bag_data` resolution logic to optionally use the `HashRingRegistry` for routing requests to specific workshop modules.

## Risk
**Failure Mode:** The `ring_state.json` file could become corrupted during a write operation if the process is interrupted.
**Mitigation:** Use a temporary file write followed by a `os.replace()` (atomic rename) to ensure the registry is either fully updated or left in its previous valid state.

**Confidence Score:** 9/10