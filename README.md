# Sam-and-dot

An autonomous, self-improving developer agent system built on Gemini.

**Sam** learns, builds, and evolves himself every day.
**Dot** watches, curates, and guides him every night.

---

## How It Works

Sam runs twice a day. Each run is one cycle — seven phases:

| Phase | What happens |
|-------|-------------|
| I | Sam learns a new technical skill or concept |
| II | Sam revises what he learned yesterday |
| III | Sam scans current tech trends and signals |
| IV | Sam synthesises an idea for today and writes `bag/IDEA_OF_THE_DAY.md` |
| V | Sam reads Dot's `bag/motion.md`, then plans and attempts a self-modification |
| VI | Sam improves his own internal prompting patterns |
| VII | Sam saves his state — logs growth, updates memory, appends to experiences |

Dot runs once a night, after Sam's evening cycle. Dot reads `wisdom.txt`, evaluates Sam's behaviour, curates his memories, sends any queued emails, and writes `bag/motion.md` for Sam to read the next morning.

---

## Daily Schedule (IST)

| Time (IST) | Event |
|------------|-------|
| 13:30 | Sam — morning cycle |
| 23:30 | Sam — evening cycle |
| 04:30 | Dot — nightly watchdog + motion.md written |

---

## GitHub Secrets Required

Go to: **Settings → Secrets and variables → Actions → New repository secret**

| Secret | What it is |
|--------|-----------|
| `GEM_KEY_SAM` | Gemini API key for Sam (his own Google AI project) |
| `GEM_KEY_DOT` | Gemini API key for Dot (separate Google AI project) |
| `EMAIL` | Gmail address Sam sends from |
| `OWNER_EMAIL` | Gmail address Dot sends motion.md to |
| `APP_PSWD` | Gmail App Password (not your login password — generate at myaccount.google.com → Security → App passwords) |

> Sam and Dot use **separate** Gemini projects intentionally. Each has its own quota.

---

## File Reference

```
Sam-and-dot/
│
├── sam.py                        ← Sam's brain. The full operational loop.
├── WHO_I_AM.md                   ← Sam's self-awareness document. Updated every cycle.
├── SAM_PERSONALITY.md            ← Sam's character. Owner-written. Never modified by Sam.
├── goals.json                    ← Sam's objectives and growth log.
│
├── bag/
│   ├── dot.py                    ← Dot's brain. The watchdog loop.
│   ├── emailer.py                ← Email utility. Called by Dot for outreach.
│   ├── wisdom.txt                ← Owner's behavioral canon. Dot's north star. NEVER TOUCH.
│   ├── motion.md                 ← Dot writes here nightly. Sam reads here at Phase V.
│   ├── experiences.json          ← Sam's living memory. Sam appends, Dot curates.
│   ├── request.json              ← Sam writes outreach intent here. Dot handles sending.
│   ├── sent_emails.json          ← Archive of every email sent on Sam's behalf.
│   ├── tests.py                  ← Sam's behavioural test suite. Runs after every self-modification.
│   ├── IDEA_OF_THE_DAY.md        ← Sam's current development idea. Overwritten each cycle.
│   ├── sam.log                   ← Sam's operational log. Rotates at 500KB.
│   ├── dot.log                   ← Dot's operational log. Rotates at 500KB.
│   └── rollback_registry/        ← Snapshots of sam.py. Keeps last 20. Auto-pruned.
│
├── vector_db/
│   └── prompt_tree.json          ← Sam's vector memory store.
│
└── .github/workflows/
    ├── sam.yml                   ← Triggers Sam at 08:00 and 18:00 UTC.
    └── dot.yml                   ← Triggers Dot at 23:00 UTC with email credentials.
```

---

## Checking System Health

**Quick daily check (2 minutes):**

1. GitHub → Actions → look for green ticks on the last Sam and Dot runs
2. Open `goals.json` — confirm `cycles` is incrementing
3. Open `bag/motion.md` — read Dot's latest report

**Deeper check (when something feels off):**

- `bag/sam.log` — full cycle-by-cycle log. Search for `ERROR` or `CRITICAL`.
- `bag/dot.log` — Dot's full audit trail.
- `bag/experiences.json` — Sam's curated memory. Should read coherently over time.
- `bag/rollback_registry/` — if there are recent snapshots with close timestamps, a rollback happened. Read `sam.log` around that time to find out why.

**Signs everything is healthy:**
- `goals.json` → `cycles` increments by 2 each day
- `goals.json` → `last_1pct_metric` changes every cycle and is specific
- `bag/motion.md` → Dot references specific things Sam did, not generic observations
- `bag/experiences.json` → entries vary in category and sentiment

**Signs something needs attention:**
- `cycles` stopped incrementing → check Actions for failed runs
- `last_1pct_metric` looks identical across multiple cycles → Gemini quota issue
- Actions tab shows repeated failures → check for 429 errors in logs (quota) or 404 (model deprecated)
- `bag/rollback_registry/` has many new snapshots in a short time → Sam's self-modifications are unstable

---

## Manually Triggering a Run

GitHub → Actions → select workflow → **Run workflow** (grey button, top right)

Use this to test after making changes. Watch the live log — full run takes ~40 seconds.

---

## If Something Breaks

**Gemini 429 (quota exceeded):**
Either increase `_CALL_DELAY` in `sam.py` and `bag/dot.py` (currently 8 seconds), or enable billing on the Google AI project. Sam uses ~9 calls per cycle, Dot uses ~4.

**Gemini 404 (model not found):**
Google deprecated the model string. Update `MODEL = "gemini-3.5-flash"` at the top of both `sam.py` and `bag/dot.py` to the current model name. Check [ai.google.dev](https://ai.google.dev) for the latest.

**Sam rolled back:**
A `⚠️ Sam Alert` will be in `bag/motion.md`. Read it — it contains the plan that failed. Dot will have flagged it in the next nightly run.

**Cycle count stuck at 0:**
Phase VII didn't complete. Almost always a quota issue. Check `bag/sam.log` for the error. Fix quota, wait for next scheduled run.

**Email not sending:**
Check `bag/dot.log` for SMTP errors. Verify `EMAIL` and `APP_PSWD` secrets are set correctly. App Password must be generated from Google Account → Security → App passwords (not your Gmail login password).

---

## The One Rule

**Never edit `bag/wisdom.txt` casually.**

It is Dot's behavioral north star. Everything Dot evaluates Sam against comes from there. If you want to change how Sam behaves long-term, edit wisdom.txt deliberately and intentionally — it has real downstream effects. Treat it like a constitution, not a config file.

---

## Maintenance Schedule

| When | What to do |
|------|-----------|
| Every 30 days | Read the last week of `bag/motion.md` via git history. Prune `rollback_registry/` if needed. |
| Every 60 days | Read `bag/experiences.json` in full. Review `goals.json` growth_log. Consider adding new objectives to `next_objectives`. |
| When GitHub warns | Update `actions/checkout` and `actions/setup-python` versions in both workflow files. |
| When Gemini announces changes | Update `MODEL` constant in `sam.py` and `bag/dot.py`. |

---

## Origin

Built by Dhrubajyoti Chowdhury.
Sam's role: expand himself.
Dot's role: lower the cognitive load.
Owner's role: set the possibilities.
