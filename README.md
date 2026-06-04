# Sam-and-dot: The World

An autonomous, self-improving developer agent system built on Gemini.

**Sam** is an eager learner and inventor (Nobita); **Dot** is his Doraemon, watching and guiding him.
This repository implements the **"World" architecture**, where agents live in their own homes and communicate via mail.

---

## The World Structure

```
Sam-and-dot/
├── README.md
├── requirements.txt
├── .github/workflows/           # Automation
└── World/
    ├── mail/                    # Post office
    │   ├── dot_to_sam/          # Sam's inbox
    │   └── sam_to_dot/          # Dot's inbox
    ├── Sam/                     # Sam's home
    │   ├── sam.py               # Intelligence Loop
    │   ├── My_memories/         # Long-term state
    │   ├── bag/                 # Governance & Infra
    │   ├── workshop_bench/      # Craft & experiments
    │   └── Others/              # Local storage
    └── Dot/                     # Dot's home
        ├── dot.py               # Watchdog
        ├── bag/                 # Wisdom mirror
        ├── Memory/              # Patterns & Archives
        ├── tests/               # Validation suite
        └── hardware/            # Communication tools
```

## How It Works

1.  **Sam** runs twice a day. He checks his inbox (`World/mail/dot_to_sam/`), learns new skills, synthesizes ideas, and self-modifies his code. He archives read letters into his `chest`.
2.  **Dot** runs throughout the day. She reads Sam's alerts in `World/mail/sam_to_dot/`, evaluates his code against the `wisdom.txt`, runs behavioral tests, and writes helpful letters back to Sam.

## GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `GEM_KEY_SAM` | Gemini API key for Sam |
| `GEM_KEY_DOT` | Gemini API key for Dot |
| `EMAIL` | Gmail address for Dot |
| `OWNER_EMAIL` | Destination for Dot's reports |
| `APP_PSWD` | Gmail App Password |

## Checking System Health

-   **GitHub Actions:** Look for green ticks on Sam and Dot workflows.
-   **Mail:** Read the letters in `World/mail/` to see the conversation between Sam and Dot.
-   **Memories:** Check `World/Sam/My_memories/experiences.json` for Sam's growth.

---
Built by Dhrubajyoti Chowdhury.
