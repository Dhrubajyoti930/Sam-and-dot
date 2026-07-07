## Scratchpad

**Option 1: Implementing a `Protocol`-based framing layer for TCP streams.**
*   *Concept:* Create a `FramingProtocol` class that handles length-prefixing and buffering for raw TCP streams, as identified in the cycle's skill learning.
*   *Critique:* This directly addresses the "framing" weakness in TCP stream handling. It is highly maintainable and modular.
*   *Trade-off:* Requires careful management of `asyncio.Transport` buffers to avoid memory bloat.

**Option 2: Integrating `Instructor` for structured LLM output in `ask_gemini`.**
*   *Concept:* Refactor `_parse_gemini_json` to use `Instructor` and Pydantic models for all LLM-to-JSON interactions.
*   *Critique:* This would significantly reduce "prompt fragility" and eliminate the need for manual regex-based JSON extraction.
*   *Trade-off:* Adds a dependency on `Instructor` and `Pydantic`. While robust, it might be overkill for simple tasks if not managed carefully.

**Selection:** Option 1 is more aligned with the current "high-performance" focus and the specific skill learned this cycle. It builds on the `asyncio.Protocol` foundation without adding external dependencies.

---

## Idea: `LengthPrefixedProtocol` Implementation
Develop a robust `asyncio.Protocol` subclass that implements length-prefixed message framing to ensure reliable data reconstruction over TCP streams.

## Why
TCP is a stream-oriented protocol; `data_received` may trigger multiple times for one message or once for multiple messages. Without explicit framing, the system is prone to partial-message corruption. This implementation provides the necessary infrastructure for high-throughput, reliable communication.

## Implementation Steps
1.  **Define `LengthPrefixedProtocol`:** Subclass `asyncio.Protocol` with a `bytearray` buffer.
2.  **Implement `data_received`:** Append incoming data to the buffer; check if the buffer contains a full length-prefixed frame (e.g., 4-byte header).
3.  **Add Flow Control:** Implement `pause_writing` and `resume_writing` to respect the transport's high/low watermarks.
4.  **Lifecycle Management:** Explicitly handle `connection_lost` and `eof_received` to clear buffers and prevent socket leaks.

## Risk
*   **Failure Mode:** Buffer overflow if the client sends massive messages without respecting backpressure, or if the length-prefix is malformed.
*   **Mitigation:** Implement a `MAX_MESSAGE_SIZE` constant and immediately close the connection if a received length-prefix exceeds this limit.
*   **Confidence Score:** 9/10. The pattern is well-understood, and the `asyncio` documentation provides clear hooks for this exact use case.