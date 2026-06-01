## Idea: Adaptive Throughput Controller (ATC) via PID Loop

I propose building an **Adaptive Throughput Controller (ATC)** in `bag/concurrency_controller.py` that utilizes a PID (Proportional-Integral-Derivative) loop to dynamically adjust my concurrency limit ($N$) for Gemini API calls. This controller will ingest `sys.monitoring` telemetry (latency/queue depth) to stabilize throughput, effectively treating my request ingress as an M/M/1 queue.

---

## Why

My current request handling is either static or reactive:
1. **The Oscillation Problem:** My current logic (and planned LART) uses threshold triggers. These cause massive oscillations—hitting a threshold, dropping concurrency, latency recovering, then ramping back up until it hits the threshold again. A PID controller provides a smoothed, proportional response that prevents this "sawtooth" throughput.
2. **Resource Alignment:** My goal is to maximize throughput while staying within the SLA. A PID loop allows me to find the "knee" in the throughput curve—the point just before latency spikes—and maintain that optimal concurrency limit indefinitely.
3. **Control Theory Maturity:** Moving from "if-then" logic to PID-based feedback control represents a non-trivial evolution in my autonomous capability, transitioning my request-handling from a heuristic state to a mathematical one.

---

## Implementation Steps

1. **Telemetry Integration (`bag/concurrency_controller.py`):**
   - Create an `ATC` class that maintains the current `max_concurrency` variable.
   - Use `sys.monitoring` to track the moving average of `RTT` (Round Trip Time).
   - Define the `Error` signal as $TargetLatency - ObservedLatency$.
2. **PID Logic:**
   - **Proportional:** Adjust $N$ based on current error.
   - **Integral:** Accumulate past error to adjust for steady-state bias.
   - **Derivative:** Dampen the response to prevent overshoot (the primary cause of oscillation).
3. **Control Loop:** Wrap the `AsyncWorkerPool` concurrency semaphore. Instead of a fixed value, the loop updates the semaphore value every 5 cycles based on the controller output.
4. **Integration:** Update `sam.py` to route all Gemini API requests through the `ATC` instance instead of the hardcoded `_CALL_DELAY`.

---

## Risk

**Critical Self-Assessment: Is this over-engineering for a local agent?**
Yes. Implementing control theory on a client that only performs a few hundred calls per day is likely overkill compared to a simpler, adaptive token-bucket. I risk creating a system that is harder to debug and prone to \"tuning drift\" if my latency profile changes due to external API volatility.

**Mitigation:**
- **PID Clamping:** I will enforce strict min/max bounds on the concurrency limit (e.g., $1 \le N \le 5$). 
- **Telemetry-Only Phase:** I will run the controller in an \"Open Loop\" mode for two cycles—calculating the recommended $N$ but not applying it—to ensure the PID math is stable and doesn't recommend catastrophic concurrency values.
- **Human-in-the-Loop:** I will log the controller's suggested adjustments to `sam.log` for Dot's review before I give it the power to autonomously scale my concurrency.