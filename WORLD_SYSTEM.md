# 🌍 The Sam-and-Dot World System
_Complete Technical & Narrative Architecture_

Welcome to the **World Architecture**. This project has evolved from a flat script into a multi-agent ecosystem designed for absolute autonomy, safety, and continuous growth.

---

## 🏗️ 1. Directory Structure: The "Home" Concept

The project is divided into physical areas that represent the roles and privacy of each agent.

### `World/Sam/` (Sam's Home)
*   **`sam.py`**: The Central Intelligence Loop. Sam's "Heartbeat."
*   **`My_memories/`**: Sam's brain storage (`goals.json`, `experiences.json`, `knowledge_log.json`).
*   **`bag/`**: Sam's permanent toolkit (Hardened logic for patching, versioning, and stability).
*   **`workshop_bench/`**: Where Sam builds new things. He can move files here, delete prototypes, and refactor code.
*   **`Gemini_note_pad/`**: Where Sam's system prompts live. He can evolve his own way of thinking here (PROMPT_VERSION).
*   **`chest/`**: Sam's private archive for letters and snapshots.

### `World/Dot/` (Dot's Station)
*   **`dot.py`**: The Watchdog Loop. Runs once a day to mentor Sam.
*   **`tests/`**: Dot owns the **Behavioural Integrity Tests**. She uses these to verify Sam hasn't broken himself.
*   **`hardware/`**: Dot's tools for interacting with the owner (Emailer).
*   **`Memory/`**: Dot's private archive of alerts she received from Sam.

### `World/mail/` (The Post Office)
*   **`sam_to_dot/`**: Letters and alerts Sam sends to Dot.
*   **`dot_to_sam/`**: Guidance and feedback Dot sends to Sam.
*   *Note: All letters are timestamped and archived after reading to prevent clutter.*

---

## 🔄 2. The 7-Phase Operational Lifecycle (Sam)

Sam follows a rigid sequence every time he wakes up to ensure he grows without breaking.

1.  **Phase I: Deep Learning**: Sam picks a topic from his `next_objectives` and masters it.
2.  **Phase II: Spaced Repetition**: Sam reviews a topic from 5 days ago to ensure the knowledge is retained in his code.
3.  **Phase III: Market Ingestion**: Sam scans the tech world for trends and verifies the URLs are real (Hallucination protection).
4.  **Phase IV: Synthesis**: Sam combines his new skill + market data into a unique **IDEA_OF_THE_DAY.md**.
5.  **Phase V: Development**: Sam reads Dot's mail and applies a **Surgical Patch** to his codebase to implement the idea.
6.  **Phase VI: Cognitive Evolution**: Sam critiques his own prompts and applies a micro-patch to his "brain" to think better.
7.  **Phase VII: State Saving**: Sam records his "1% Growth Metric" and updates his identity anchor.

---

## 🛡️ 3. Robustness & Safety (The "Never-Break" Shield)

We have implemented four layers of protection to ensure the agents survive Gemini's quirks.

### 🔌 Model Fallback & Rotation
If the primary model (`gemini-3.1-flash-lite`) is down or limited, the system proactively decelerates and retries with aggressive RPM protection.

### 🧪 Integrity Gates
*   **Syntax Check**: Sam won't apply a change if the Python code doesn't compile.
*   **Behaviour Check**: Sam won't apply a change if Dot's tests fail.
*   **Rollback Snapshot**: Sam takes a full backup of his body before every change. If anything fails, he instantly reverts to the last healthy state.

### 📦 Surgical Patching
Sam never rewrites whole files. He uses a `JSON Patch Engine` to replace only specific lines. This prevents "AI Laziness" where the model might cut off the rest of the code.

### 🧹 State Hygiene
The system automatically trims history. `goals.json` is kept under 2KB by moving heavy memories to `experiences.json`, ensuring Sam stays fast and responsive.

---

## 📡 4. Communication: The "Distant God" Protocol

You (The Owner) are the Distant God.
*   **Dot** writes to you every night via email.
*   **Sam** occasionally requests to reach out to real developers in the world (with your approval).
*   You influence the World by editing **`wisdom.txt`** (The Constitution) or **`SAM_PERSONALITY.md`** (The Soul).

---

**This World is built for a 1000-day journey. Push it to the cloud and watch it evolve.** 🚀🌬️️
