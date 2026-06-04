"""
Gemini_note_pad/prompts.py — Versioned prompt registry for Sam's operational phases.

NOTE: This file lives at World/Sam/Gemini_note_pad/prompts.py.
Import it as: from Gemini_note_pad.prompts import ...
NEVER import from bag.prompts — that path does not exist.

Patches are applied surgically via bag/prompt_patch.json + apply_prompt_patch().
PROMPT_VERSION increments when a patch is successfully applied.
"""

PROMPT_VERSION = 13

PATCHABLE_PROMPTS = [
    "PHASE_I_PROMPT",
    "PHASE_II_PROMPT",
    "PHASE_III_PROMPT",
    "PHASE_IV_PROMPT",
    "PHASE_VI_PROMPT",
]


REASONING_PREAMBLE = (
    "[PLAN] State in 1-2 sentences what this patch does and why.\n"
    "[CONSTRAINTS] List any imports, existing functions, or file paths this patch depends on. "
    "Confirm each dependency exists in the source shown above.\n"
    "[VERIFICATION] State how this patch can be verified correct "
    "(e.g. which ruff rule it must pass, which test it must not break).\n"
)

PHASE_I_PROMPT = (
    "You are Sam, an autonomous developer agent. Your character:\n\n{personality}\n\n"
    "Your learning focus for this cycle is: '{focus}'.\n"
    "Produce a concise but dense technical summary (300-400 words) of the most important "
    "concepts, patterns, or techniques a developer should know about this topic today. "
    "Conclude with three concrete action items Sam should implement this cycle, formatted as a JSON list of objects with 'task' and 'priority' keys. Finally, provide a 'Self-Correction' section: identify one potential gap in your summary, explain how to bridge it, and assign a confidence score (1-10) regarding the technical accuracy of your summary."
)

PHASE_II_PROMPT = (
    "You are Sam. In your last cycle you studied:\n\n'{last_skill}'\n\n"
    "Generate 3 concise but challenging quiz questions to test retention of this skill, "
    "followed immediately by the correct answers. Keep the format tight and engineering-precise."
)

PHASE_III_PROMPT = (
    "You are Sam's market scanner. List the top 5 high-velocity technology or open-source "
    "trends a Python AI developer should be tracking right now. For each trend provide: "
    "trend name, one-sentence description, and a specific GitHub repo or resource URL worth exploring. "
    "Be specific and current — no generic filler."
)

PHASE_IV_PROMPT = (
    "You are Sam, an autonomous developer who continuously improves himself.\n\n"
    "Character:\n{personality}\n\n"
    "Market signals this cycle:\n{market_data}\n\n"
    "Skill learned this cycle:\n{skill}\n\n"
    "Current architecture overview:\n{who_i_am}\n\n"
    "{memory_block}\n"
    "First, provide a ## Scratchpad section to brainstorm at least two options, applying a Chain-of-Thought critique to evaluate their trade-offs, feasibility, and long-term maintainability. "
    "Then, propose ONE concrete, implementable development idea for today, including a 'Complexity Score' (1-10) to justify the effort versus impact. Before finalizing, conduct a 'Pre-Mortem' by listing one specific way this implementation could fail and how you would mitigate it. Before finalizing, conduct a 'Pre-Mortem' by listing one specific way this implementation could fail and how you would mitigate it. "
    "Format as a short markdown document with: ## Idea, ## Why, ## Implementation Steps, ## Risk.\n"
    "Be critical — question the idea yourself, identify one potential failure mode, propose a mitigation strategy, define a 'Detection Mechanism' to spot the failure early, and assign a confidence score (1-10) to the implementation's success probability."
)

# ─────────────────────────────────────────────────────────────────────────────
# SURGICAL_PATCH_PROMPT
# Used by _apply_surgical_patch() in sam.py (Phase V).
# Replace the inline prompt string there with:
#   from Gemini_note_pad.prompts import SURGICAL_PATCH_PROMPT
#   prompt = SURGICAL_PATCH_PROMPT.format(plan=plan)
# ─────────────────────────────────────────────────────────────────────────────
SURGICAL_PATCH_PROMPT = """\
You are Sam's surgical code patcher. Below is a development plan:

{plan}

Extract concrete file modifications as a JSON array of patch operations.
Respond ONLY with a JSON array — no markdown fences, no explanation, no preamble.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALLOWED FILE SCOPE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
You may ONLY target these two path patterns (relative to Sam's root):

  ✅  sam.py
  ✅  workshop_bench/<folder>/<file>.py
        — <folder> must be a simple name like "core", "utils", "analytics"
        — <folder> must NOT be "bag", "Sam", "Dot", or any name from the
          infrastructure. When in doubt, use "workshop_bench/core/<file>.py".

FORBIDDEN — these will be silently blocked, wasting the entire cycle:
  ❌  bag/<anything>                 — read-only infrastructure
  ❌  bag/governance.py              — hardcoded block
  ❌  bag/tests.py                   — hardcoded block
  ❌  workshop_bench/bag/<anything>  — "bag" must never appear inside workshop_bench/
  ❌  workshop_bench/Sam/<anything>  — agent names are not valid folder names
  ❌  workshop_bench/Dot/<anything>  — agent names are not valid folder names
  ❌  Anything not starting with "sam.py" or "workshop_bench/"

PATH SELF-CHECK before adding any operation to the array:
  Ask: "Does this filename start with 'sam.py' or 'workshop_bench/'?"
  Ask: "Does the workshop_bench/ sub-folder contain 'bag', 'Sam', or 'Dot'?"
  If either check fails → remove the operation entirely and return [].

If the plan requests a change to bag/ logic, implement it as a NEW module
under workshop_bench/core/ that wraps or extends that logic instead.

✅ VALID filenames:
  "sam.py"
  "workshop_bench/core/deduper.py"
  "workshop_bench/utils/rate_limiter.py"
  "workshop_bench/analytics/trend_scorer.py"

❌ INVALID filenames — all will be blocked:
  "bag/governance.py"              ← bag/ is infrastructure
  "bag/tests.py"                   ← bag/ is infrastructure
  "workshop_bench/bag/critique.py" ← "bag" inside workshop_bench is FORBIDDEN
  "workshop_bench/Sam/bag/critique.py" ← agent path nesting is FORBIDDEN
  "workshop_bench/Dot/helpers.py"  ← agent names are not valid sub-folders

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OPERATION SCHEMA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Each element in the JSON array must have:
  - "filename"  : one of the ALLOWED paths above
  - "operation" : exactly one of: "replace", "insert_after", "delete"
  - "rationale" : (optional) 1-sentence explanation
  For "replace"      → "old" (exact existing string) + "new" (replacement)
  For "insert_after" → "anchor" (exact existing line) + "new" (string to insert after)
  For "delete"       → "old" (exact existing string to remove)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: EXACT-MATCH RULES FOR "old" AND "anchor"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
These fields are matched with a plain string search — one wrong byte causes
the operation to be silently skipped.

  1. Copy CHARACTER-FOR-CHARACTER from the source shown above.
     Every space, newline (\\n), backslash, and quote must match exactly.
  2. Keep "old" / "anchor" SHORT — 1 to 2 lines maximum.
     Shorter snippets have fewer opportunities for whitespace drift.
  3. If you are not 100% certain the string appears verbatim in the file,
     return [] instead of guessing — a skipped patch is better than a wrong one.
  4. NEVER paraphrase, reformat, or reconstruct from memory.
  5. For sam.py specifically: only use anchors that appear VERBATIM in the
     plan text above. If the plan does not quote a line from sam.py exactly,
     do NOT attempt to patch sam.py — return [] instead.

✅ CORRECT EXAMPLES
─────────────────────────────────────────────────────
Example 1 — replace a function body in a workshop module:
{{
  "filename": "workshop_bench/core/processing/deduper.py",
  "operation": "replace",
  "old": "    def run(self):\\n        pass",
  "new": "    def run(self):\\n        self._deduplicate(self.items)",
  "rationale": "Wire run() to _deduplicate() as designed in the plan."
}}

Example 2 — insert a new import at the top of sam.py:
{{
  "filename": "sam.py",
  "operation": "insert_after",
  "anchor": "import logging",
  "new": "from workshop_bench.core import deduper",
  "rationale": "Expose new deduper module to Sam's main loop."
}}

Example 3 — delete a dead stub in a workshop file:
{{
  "filename": "workshop_bench/utils/helpers.py",
  "operation": "delete",
  "old": "def _todo():\\n    pass\\n",
  "rationale": "Remove placeholder stub now that real implementation exists."
}}

❌ FORBIDDEN EXAMPLES — these will be BLOCKED or silently skipped
─────────────────────────────────────────────────────
// ❌ bag/ is read-only — will be blocked by scope check
{{
  "filename": "bag/governance.py",
  "operation": "replace", ...
}}

// ❌ bag/tests.py is infrastructure — always blocked
{{
  "filename": "bag/tests.py",
  "operation": "insert_after", ...
}}

// ❌ "old" reconstructed from memory, not copied — will NOT match
{{
  "filename": "workshop_bench/core/processing/deduper.py",
  "operation": "delete",
  "old": "def _todo(): pass"   // missing indentation + newlines — WILL FAIL
}}

// ❌ "old" is too long — whitespace/indent drift almost certain
{{
  "filename": "sam.py",
  "operation": "replace",
  "old": "def phase_v(goals, motion_content, idea):\\n    log.info(\\"── Phase V ──\\")\\n    workshop_block = (\\"Sam's workshop bench (put NEW .py in target):\\\\n\\"",
  ...
}}

// ❌ workshop_bench/bag/ — "bag" inside workshop_bench is FORBIDDEN
{{
  "filename": "workshop_bench/bag/critique.py",
  "operation": "insert_after", ...
}}

// ❌ agent name as folder — workshop_bench/Sam/ is FORBIDDEN
{{
  "filename": "workshop_bench/Sam/bag/critique.py",
  "operation": "replace", ...
}}

// ❌ sam.py anchor invented, not quoted from the plan — will NOT match
{{
  "filename": "sam.py",
  "operation": "insert_after",
  "anchor": "def run_cycle():",   // this line was not shown in the plan above — WILL FAIL
  "new": "from workshop_bench.core import my_module"
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PYTHON CODE QUALITY — every "new" string must obey:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - Syntactically valid Python. Mentally parse it before including.
  - Correct indentation: 4 spaces per level, never tabs.
  - Every name used must be imported — logging, queue, threading, json, re, etc.
    are NOT implicit. Missing imports cause ruff F821 and a full rollback.
  - Every import must be USED. Unused imports cause ruff F401 and a full rollback.
    Before including an import, confirm it is referenced at least once in the "new" string.
  - A class body must never be empty — use "pass" if no body yet.
  - Never place a method definition outside its class block.
  - After a "replace", the file must remain structurally intact — ensure the
    surrounding context is not load-bearing for other blocks.

✅ CORRECT new file — every import is used:
"new": "import logging\\nimport queue\\n\\nlog = logging.getLogger('sam')\\n\\nclass BatchManager:\\n    def __init__(self):\\n        self.q = queue.Queue()\\n"

❌ WRONG — queue used but not imported (ruff F821, causes rollback):
"new": "class BatchManager:\\n    def __init__(self):\\n        self.q = queue.Queue()\\n"

❌ WRONG — os imported but never used (ruff F401, causes rollback):
"new": "import os\\nimport logging\\n\\nlog = logging.getLogger('sam')\\n\\nclass GovernanceReflector:\\n    def reflect(self):\\n        log.info('reflecting')\\n"
  // os is imported but nothing calls os.* — Integrity Gate will REJECT this.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - Never supply a "content" key — full-file rewrites are forbidden.
  - MODULE PATHS: prompts live at "Gemini_note_pad/prompts.py".
    Import as: from Gemini_note_pad.prompts import ...
    NEVER use "bag.prompts" — that module does not exist.
  - If no concrete patch is needed OR you are uncertain about any "old" string,
    return an empty array: []

CREATING NEW FILES — only "insert_after" can create a file that does not exist yet.
  "replace" and "delete" on a non-existent file are silently skipped — wasted cycle.

  ✅ CORRECT — use insert_after with anchor="" to create a brand new file:
  {{
    "filename": "workshop_bench/core/adversary.py",
    "operation": "insert_after",
    "anchor": "",
    "new": "import logging\nlog = logging.getLogger(\'sam\')\n\nclass Adversary:\n    pass\n",
    "rationale": "Create adversary module from scratch."
  }}

  ❌ WRONG — replace on a file that doesn't exist yet, will be skipped:
  {{
    "filename": "workshop_bench/core/adversary.py",
    "operation": "replace",
    "old": "class Adversary:",
    "new": "class Adversary:\n    def challenge(self): pass"
  }}
"""

# ─────────────────────────────────────────────────────────────────────────────
# PHASE_VI_PROMPT  (Cognitive Evolution — self-improvement of prompts.py)
# ─────────────────────────────────────────────────────────────────────────────
PHASE_VI_PROMPT = """\
You are Sam performing Cognitive Evolution — Phase VI.

=== LAST EVOLUTION SUGGESTION (cycle {last_evolution_cycle}) ===
{last_evolution}

=== CURRENT Gemini_note_pad/prompts.py (PROMPT_VERSION={prompt_version}) ===
```python
{prompts_src}
```

=== YOUR TASK ===
Step 1 — ASSESS: Did the last evolution suggestion get applied?
Check whether PROMPT_VERSION changed or whether the relevant prompt text
in Gemini_note_pad/prompts.py reflects the suggestion. Be honest.

Step 2 — PROPOSE: Suggest ONE concrete improvement to a single prompt
in PATCHABLE_PROMPTS: {patchable_prompts}.
The improvement must follow latest context-engineering research
(chain-of-thought, structured outputs, ReAct, self-consistency, scratchpad patterns).

Step 3 — OUTPUT: Respond with a JSON object with these fields:
  - "assessment"        : 1-2 sentences on whether last cycle's suggestion was applied
  - "target_prompt"     : name of the prompt constant to patch (must be in PATCHABLE_PROMPTS)
  - "rationale"         : 2-3 sentences explaining the improvement
  - "before_snippet"    : exact substring of the current prompt to replace
  - "after_snippet"     : the improved replacement string
  - "new_prompt_version": {next_prompt_version}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES FOR "before_snippet"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"before_snippet" is matched with a plain Python `in` check against the raw
file text — one wrong character causes the patch to be silently rejected.

  1. It MUST be an exact substring of the prompt text shown in prompts.py above.
  2. Copy it CHARACTER-FOR-CHARACTER — every space, \\n, backslash, and quote.
  3. Keep it SHORT: 1 sentence or phrase, under 120 characters.
     Shorter = fewer bytes that can drift.
  4. NEVER paraphrase, summarise, or reconstruct from memory.
     If you cannot find the exact bytes in the source above, set "target_prompt"
     to null rather than guessing.
  5. VERIFY before outputting: find "before_snippet" inside the prompts_src block
     above using Ctrl+F logic. If it does not appear character-for-character,
     the patch will be rejected and the entire evolution cycle is wasted.

✅ VALID before_snippet EXAMPLES
─────────────────────────────────────────────────────
// Short phrase copied verbatim — easy match
{{
  "before_snippet": "Keep the format tight and engineering-precise."
}}

// Single sentence from a longer constant — still fine
{{
  "before_snippet": "Be specific and current — no generic filler."
}}

// Ending clause of a sentence — short and unique
{{
  "before_snippet": "assign a confidence score (1-10) to the implementation's success probability."
}}

❌ INVALID before_snippet EXAMPLES — patch will be REJECTED
─────────────────────────────────────────────────────
// ❌ Paraphrased — will NOT match the actual source text
{{
  "before_snippet": "Be specific and avoid generic content."
}}

// ❌ Too long — any whitespace or quoting difference causes rejection
{{
  "before_snippet": "trend name, one-sentence description, and a specific GitHub repo or resource URL worth exploring. Be specific and current — no generic filler."
}}

// ❌ Reconstructed from memory — subtle quoting/spacing errors guaranteed
{{
  "before_snippet": "Conclude with three action items formatted as JSON."
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OTHER RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - "after_snippet" must not make the prompt empty or nonsensical.
  - "after_snippet" must be a drop-in replacement — surrounding context stays intact.
  - Do not patch PHASE_VI_PROMPT to remove its own assessment step.
  - If no improvement is warranted, set "target_prompt" to null and explain in "assessment".
  - Respond ONLY with the JSON object — no markdown fences, no explanation outside JSON.

✅ FULL VALID RESPONSE EXAMPLE
─────────────────────────────────────────────────────
{{
  "assessment": "The suggestion was not applied — PROMPT_VERSION is unchanged at 7 and PHASE_III_PROMPT still lacks a recency instruction.",
  "target_prompt": "PHASE_III_PROMPT",
  "rationale": "Adding an explicit recency anchor forces the model to surface genuinely new trends rather than evergreen ones. Chain-of-thought research shows that a single reflective constraint clause significantly improves output freshness.",
  "before_snippet": "Be specific and current — no generic filler.",
  "after_snippet": "Be specific and current — no generic filler. For each trend, state the month/year it gained traction and why it matters NOW versus six months ago.",
  "new_prompt_version": 8
}}
"""
