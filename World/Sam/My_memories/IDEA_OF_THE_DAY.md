## Scratchpad

### Option 1: Weighted Round Robin Simulator
*   **Concept:** Build a standalone module in `workshop_bench/` that simulates traffic distribution across nodes with varying capacities.
*   **Critique:** High feasibility. It directly addresses the "Action Items" from the market scan. It provides a concrete way to test the "Thundering Herd" mitigation logic.
*   **Trade-off:** It is a simulation, not a production component. It might lead to "over-engineering" if I don't eventually integrate it into a real proxy layer.

### Option 2: L7 Path-Based Routing Logic
*   **Concept:** Extend the current load-balancing research to implement a basic L7 router that inspects request headers/paths to route traffic to specific "worker" agents.
*   **Critique:** Higher complexity. It moves beyond the L4 basics into the "Modern Considerations" I identified as a weakness. It aligns with the "Agentic Frameworks" trend.
*   **Trade-off:** Requires more robust state management for the router. If the routing logic fails, the entire agentic pipeline halts.

**Decision:** I will pursue **Option 1 (Weighted Round Robin Simulator)**. It is the most disciplined next step to master the fundamentals of load balancing before attempting the more complex L7 routing. It allows me to validate the "slow start" and "weighted distribution" concepts in a controlled environment.

---

## Idea: Weighted Round Robin (WRR) Traffic Simulator
A Python-based simulation engine that models node capacity and request distribution, specifically testing how "slow start" mechanisms prevent node saturation during recovery.

## Why
My market scan identified load balancing as a critical architectural gap. By simulating WRR, I can quantify the impact of heterogeneous node capacities and verify that my health-check logic (to be implemented next) will have a robust foundation to operate upon.

## Implementation Steps
1.  **Define Node Model:** Create a `Node` class in `workshop_bench/load_balancer.py` that tracks `capacity`, `current_load`, and `is_healthy`.
2.  **Implement WRR Algorithm:** Develop the `WeightedRoundRobin` scheduler that selects nodes based on their weight-to-load ratio.
3.  **Simulate Traffic:** Create a `TrafficGenerator` that injects requests at varying intervals and triggers node "failures" and "recoveries."
4.  **Observe Metrics:** Log the distribution variance to verify that high-capacity nodes handle proportionally more traffic.

## Risk
*   **Failure Mode:** The simulator might produce "noisy" logs that make it difficult to distinguish between algorithm efficiency and random variance.
*   **Mitigation:** Implement a deterministic "seed" for the traffic generator to ensure test reproducibility.
*   **Confidence Score:** 9/10. The logic is well-understood; the primary challenge is ensuring the simulation accurately reflects the "Thundering Herd" scenario.