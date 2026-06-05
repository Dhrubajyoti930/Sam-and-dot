# Sam & Dot 🤖✉️

Two AI agents living in GitHub Actions. No bloat. Mild humor.

---

## Agents

### Sam (`sam.py`)
The creative one. Sam:
1. Gets an idea (from `idea_queue.json` or generates one)
2. Decides if an existing script fits → runs it
3. Otherwise: makes a plan, creates modules/scripts, runs the result

### Dot (`dot.py`)
The communicator. Dot:
1. Reads incoming messages / emails
2. Extracts ideas → feeds them to `idea_queue.json`
3. Searches Sam's scripts/modules for relevant work
4. Generates replies to strangers
5. Sends daily summary to owner

---

## Structure

```
.github/workflows/
  sam.yml          # Runs Sam once on push
  dot.yml          # Runs Dot once on push

modules/
  __init__.py      # Tag registry loader
  _starter_pack.py # Core utility functions
  s_example.py     # Example Sam module

scripts/
  s_example_script.py  # Example Sam script

sam.py             # Sam agent entrypoint
dot.py             # Dot agent entrypoint
idea_queue.json    # Shared idea queue
tag_registry.json  # Module + script tagline registry
```

---

## Conventions

| What | Convention |
|------|-----------|
| Starterpack functions | `_lowercase_with_underscores()` |
| Sam's functions | `S_CAPS_WITH_UNDERSCORES()` |
| Module names | `s_module_name.py` |
| Script names | `s_name_script.py` |
| Max lines per function | 30 |
| Max functions per module | 4 |

---

## Tagline Format

Every module and script has a tagline stored in `tag_registry.json`. Gemini reads taglines to understand what each module does and wire them together.

**Module tagline format:**
```
module | s_name | theme:X | funcs: FUNC(param:type)->return, ... | purpose: description
```

**Script tagline format:**
```
script | s_name_script | purpose: what it does
```

---

## GitHub Secrets Required

| Secret | Used by |
|--------|---------|
| `GEM_KEY_SAM` | Sam's Gemini API key |
| `GEM_KEY_DOT` | Dot's Gemini API key |
| `SPARE_KEY` | Fallback Gemini key (used by Sam if GEM_KEY_SAM fails) |
| `OWNER_EMAIL` | Where Dot sends summaries |
| `EMAIL` | Dot's Gmail address |
| `APP_PSWD` | Gmail app password for Dot |

---

## How to Add an Idea

Edit `idea_queue.json` directly:
```json
{
  "ideas": [
    { "idea": "Generate a daily haiku about the weather", "timestamp": 0 }
  ]
}
```

Or let Dot extract one from an incoming message automatically.

---

*Sam builds. Dot talks. Together they ship.*
