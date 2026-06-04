"""
dot.py — Watchdog & Support Agent
Project Sam-and-dot

Dot runs five times a day (01:30, 03:30, 05:30, 07:30, 09:30 UTC).
Dot is Sam's conscience, archaeologist, memory curator, and postmaster.

What Dot does each run:
  1.  Wisdom check   — evaluate sam.py against wisdom.txt, write motion.md
  2.  Experiences    — curate experiences.json (keep/consolidate/forget)
  3.  Email dispatch — if request.json is pending, compose & send HTML email
  4.  Bag excavation — rehabilitate broken experiments in bag/
  5.  Sunday only    — check inbox for replies, summarise to motion.md
"""

import os
import re
import json
import time
import imaplib
import email as emaillib
import datetime
import logging
import logging.handlers
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
DOT_DIR     = Path(__file__).parent.resolve()
ROOT        = DOT_DIR.parent.resolve()  # World/
SAM_DIR     = ROOT / "Sam"
MAIL_IN     = ROOT / "mail" / "sam_to_dot"
MAIL_OUT    = ROOT / "mail" / "dot_to_sam"

BAG         = DOT_DIR / "bag"
WISDOM      = BAG / "wisdom.txt"
SAM_PY      = SAM_DIR / "sam.py"
GOALS       = SAM_DIR / "My_memories" / "goals.json"
OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "")


def _bag_data(key: str) -> Path:
    from bag.bag_paths import resolve
    return resolve(BAG, key)

# ── Logging ──────────────────────────────────────────────────────────────────
BAG.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [DOT][%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(BAG / "dot.log", maxBytes=500_000, backupCount=3),
    ],
)
log = logging.getLogger("dot")

# ── Gemini client (Dot's OWN independent instance) ───────────────────────────
from google import genai  # noqa: E402
from hardware.emailer import send_html_email  # noqa: E402

GEM_KEY = os.environ.get("GEM_KEY_DOT")
if not GEM_KEY:
    raise EnvironmentError("GEM_KEY_DOT secret is not set.")
CLIENT = genai.Client(api_key=GEM_KEY)

MODEL = "gemini-3.1-flash-lite"

# Set to False to run Sunday tasks every cycle (testing); True for production
SUNDAY_ONLY = True

# ── Rate limiting ─────────────────────────────────────────────────────────────
_CALL_DELAY = 8  # seconds


# ── Directory Guard ─────────────────────────────────────────────────────────

def init_world():
    """Ensure every critical directory in Dot's World is built and ready."""
    directories = [
        BAG,
        DOT_DIR / "Memory",
        DOT_DIR / "Gemini_note_pad",
        DOT_DIR / "hardware",
        DOT_DIR / "tests",
        DOT_DIR / "Others",
        MAIL_IN,
        MAIL_OUT
    ]
    for d in directories:
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            log.info(f"🏗️  Dot built directory: {d.relative_to(ROOT)}")


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _parse_gemini_json(text: str) -> dict | list | None:
    """Robustly extract and parse a JSON block from Gemini's response using balanced brackets."""
    if not text:
        return None
    for start_char, end_char in [('[', ']'), ('{', '}')]:
        start = text.find(start_char)
        if start == -1:
            continue
        depth = 0
        in_string = False
        escape = False
        for i, ch in enumerate(text[start:], start):
            if escape:
                escape = False
                continue
            if ch == '\\' and in_string:
                escape = True
                continue
            if ch == '"' and not escape:
                in_string = not in_string
            if not in_string:
                if ch == start_char:
                    depth += 1
                elif ch == end_char:
                    depth -= 1
                    if depth == 0:
                        try:
                            clean = text[start:i+1]
                            clean = re.sub(r',\s*([\]\}])', r'\1', clean)
                            return json.loads(clean)
                        except Exception:
                            break
    return None


def ask_gemini(prompt: str, retries: int = 3, temperature: float = 0.2) -> str:
    from Others.semantic_cache import check_cache, update_cache, get_db, invalidate_truncated
    global _CALL_DELAY

    get_db()
    invalidate_truncated()
    cycle = int(datetime.datetime.utcnow().strftime("%Y%m%d"))

    cached = check_cache(prompt, cycle)
    if cached:
        # Validate cached response is not truncated before serving
        if not (cached.endswith("...") or (cached.count("{") > cached.count("}")) or (cached.count("[") > cached.count("]"))):
            log.info("Dot cache hit.")
            return cached
        else:
            log.warning("Cached response appears truncated — bypassing cache.")

    for attempt in range(retries):
        try:
            time.sleep(_CALL_DELAY)
            response = CLIENT.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    'max_output_tokens': 8192,
                    'temperature': temperature,
                    'top_p': 0.95
                }
            )
            if not response or not response.text:
                raise ValueError("Empty response")

            res = response.text.strip()

            # Anti-truncation check (Dot is now as strict as Sam)
            if res.endswith("...") or (res.count("{") > res.count("}")) or (res.count("[") > res.count("]")):
                 log.warning("Potential truncation detected in Dot's thought. Retrying...")
                 continue

            update_cache(prompt, res, cycle)
            return res
        except Exception as e:
            err = str(e).upper()
            if any(x in err for x in ["429", "RESOURCE_EXHAUSTED"]):
                _CALL_DELAY = min(_CALL_DELAY + 4, 30)
                time.sleep(_CALL_DELAY * (attempt + 1))
            else:
                log.error(f"Dot Gemini error: {e}")
                time.sleep(10)

    return "[Dot Gemini error: Exhausted]"


def _sleep():
    time.sleep(_CALL_DELAY)


def load_wisdom() -> str:
    if WISDOM.exists():
        return WISDOM.read_text()
    return "(wisdom.txt not found)"


def load_sam_py() -> str:
    if SAM_PY.exists():
        return SAM_PY.read_text()
    return "(sam.py not found)"


def load_goals() -> dict:
    """Read Sam's current goals from the root-level goals.json."""
    if GOALS.exists():
        try:
            with open(GOALS) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def read_sam_alerts() -> str:
    """Read any ALERT_*.md files from mail/sam_to_dot/ and archive them."""
    alerts = sorted(MAIL_IN.glob("ALERT_*.md"))
    if not alerts:
        return ""

    content_list = []
    for alert in alerts:
        content_list.append(alert.read_text(encoding="utf-8"))
        # Archive alert to Dot's Memory — ensure directory exists
        dest_dir = DOT_DIR / "Memory"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / alert.name
        alert.rename(dest)
        log.info(f"Archived Sam alert: {alert.name}")

    return "\n\n---\n\n".join(content_list)


def load_experiences() -> list:
    exp = _bag_data("experiences")
    if exp.exists():
        with open(exp) as f:
            return json.load(f)
    return []


def save_experiences(data: list):
    with open(_bag_data("experiences"), "w") as f:
        json.dump(data, f, indent=2)


def load_request() -> dict:
    req = _bag_data("request")
    if req.exists():
        try:
            return json.loads(req.read_text())
        except Exception:
            return {}
    return {}


def clear_request():
    _bag_data("request").write_text("{}")


def load_sent_log() -> list:
    sent = _bag_data("sent_emails")
    if sent.exists():
        with open(sent) as f:
            return json.load(f)
    return []


def append_sent_log(entry: dict):
    log_data = load_sent_log()
    log_data.append(entry)
    sent = _bag_data("sent_emails")
    with open(sent, "w") as f:
        json.dump(log_data, f, indent=2)


def write_motion(content: str):
    """Dot writes a new letter to mail/dot_to_sam/ each run."""
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"Letter_{ts}.md"
    header = f"# Letter from Dot — {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n"
    MAIL_OUT.mkdir(parents=True, exist_ok=True)
    (MAIL_OUT / filename).write_text(header + content, encoding="utf-8")
    log.info(f"Letter written to Sam: {filename}")


def append_motion(section_title: str, content: str):
    """Dot appends to the latest letter she wrote in this run."""
    letters = sorted(MAIL_OUT.glob("Letter_*.md"), reverse=True)
    if not letters:
        write_motion(f"## {section_title}\n\n{content}")
        return

    latest = letters[0]
    with open(latest, "a", encoding="utf-8") as f:
        f.write(f"\n\n---\n\n## {section_title}\n\n{content}")
    log.info(f"Appended to {latest.name}: {section_title}")


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 1 — WISDOM CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def wisdom_check() -> str:
    log.info("── Task 1: Wisdom Check ──")
    wisdom  = load_wisdom()
    sam_src = load_sam_py()

    # Get personality from Sam's bag
    personality_path = SAM_DIR / "bag" / "SAM_PERSONALITY.md"
    personality = personality_path.read_text() if personality_path.exists() else "(Personality not found)"

    prompt = (
        "You are Dot, an independent watchdog AI for an autonomous developer agent called Sam.\n"
        "Your behavioral north star is the owner's wisdom document below.\n\n"
        f"=== WISDOM (owner's behavioral canon) ===\n{wisdom}\n\n"
        f"=== SAM'S PERSONALITY ===\n{personality}\n\n"
        f"=== SAM'S CURRENT CODE (sam.py — full source) ===\n{sam_src}\n\n"
        "Evaluate Sam's code against the wisdom. Identify:\n"
        "1. Any behavioral deviations, sandbagging, or violations of stated principles.\n"
        "2. Positive highlights — things Sam did well this cycle.\n"
        "3. Specific, actionable suggestions for Sam's next cycle.\n"
        "4. Any flags that warrant the owner's attention.\n\n"
        "Write your findings as a clear markdown report. You influence, never command. "
        "Keep a tone of mentorship, not judgment. Be concise but precise. "
        "Always end with at least one concrete, actionable suggestion Sam can act on next cycle."
    )
    findings = ask_gemini(prompt)
    log.info("Wisdom check complete.")
    return findings


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 2 — EXPERIENCES CURATION
# ═══════════════════════════════════════════════════════════════════════════════

def curate_experiences() -> str:
    log.info("── Task 2: Experiences Curation ──")
    experiences = load_experiences()

    if not experiences:
        log.info("No experiences to curate yet.")
        return "(No experiences to curate yet — Sam hasn't completed a full cycle.)"

    _sleep()
    prompt = (
        "You are Dot, Sam's memory curator. Below is Sam's experiences.json — "
        "a log of everything Sam has lived through across his cycles.\n\n"
        f"=== EXPERIENCES ===\n{json.dumps(experiences, indent=2)}\n\n"
        "Your job:\n"
        "1. Identify which entries should be KEPT as-is (still relevant, formative).\n"
        "2. Identify which entries should be CONSOLIDATED (similar themes that can be merged).\n"
        "3. Identify which entries should be FORGOTTEN (outdated, low-value, redundant).\n"
        "4. If consolidating: write the merged entry as a single JSON object with the same fields,\n"
        "   'consolidated_from' must be a list of INTEGER cycle numbers, and updated content.\n\n"
        "Respond ONLY with a raw JSON object — no markdown fences, no preamble, no explanation.\n"
        "The first character of your response must be '{'.\n\n"
        "  - 'keep': list of integer cycle numbers to keep unchanged\n"
        "  - 'forget': list of integer cycle numbers to drop\n"
        "  - 'consolidated': list of new merged entry objects; each must have:\n"
        "      'consolidated_from': list of INTEGER cycle numbers (e.g. [3, 4])\n"
        "      plus all standard experience fields (cycle, timestamp, summary, etc.)\n"
        "  - 'summary': 2-3 sentence narrative for Sam explaining what you curated and why\n\n"
        "Be conservative — when in doubt, keep. Only forget truly redundant or outdated entries."
    )
    raw = ask_gemini(prompt)
    curation = _parse_gemini_json(raw)
    if not curation or not isinstance(curation, dict):
        log.warning("Could not parse curation result.")
        return "(Experiences curation produced unparseable output — no changes made.)"

    keep         = set(curation.get("keep", []))
    forget       = set(curation.get("forget", []))
    consolidated = curation.get("consolidated", [])
    summary      = curation.get("summary", "")

    # Priority 2.4: Protect unmentioned entries
    # consolidated_from is a list of integer cycle numbers
    mentioned = keep | forget | {c for entry in consolidated for c in entry.get("consolidated_from", []) if isinstance(c, int)}
    unmentioned = {e.get("cycle") for e in experiences if e.get("cycle")} - mentioned
    if unmentioned:
        log.warning(f"Curation: {len(unmentioned)} entries not mentioned by Gemini — keeping them: {sorted(unmentioned)}")
        keep.update(unmentioned)

    # Rebuild the list: keep retained entries + new consolidated ones
    retained = [e for e in experiences if e.get("cycle") in keep]
    ts = datetime.datetime.utcnow().isoformat()
    for c in consolidated:
        c.setdefault("timestamp", ts)
        c.setdefault("category",  "consolidated")
        retained.append(c)

    # Sort by timestamp
    retained.sort(key=lambda e: e.get("timestamp", ""))

    save_experiences(retained)
    log.info(
        f"Experiences curated: {len(keep)} kept, {len(forget)} forgotten, "
        f"{len(consolidated)} consolidated. Total now: {len(retained)}."
    )

    report = (
        f"### Memory Curation Report\n\n"
        f"**Kept:** {sorted(keep) or 'none'}\n"
        f"**Forgotten:** {sorted(forget) or 'none'}\n"
        f"**Consolidated:** {[c.get('consolidated_from') for c in consolidated] or 'none'}\n\n"
        f"**Dot's note to Sam:** {summary}"
    )
    return report


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 3 — EMAIL DISPATCH
# ═══════════════════════════════════════════════════════════════════════════════

def dispatch_email() -> str:
    log.info("── Task 3: Email Dispatch ──")

    EMAIL_ADDR = os.environ.get("EMAIL", "")
    APP_PSWD   = os.environ.get("APP_PSWD", "")

    if not EMAIL_ADDR or not APP_PSWD:
        log.warning("EMAIL or APP_PSWD secrets not set — skipping email dispatch.")
        return "(Email dispatch skipped: credentials not configured.)"

    request = load_request()
    if not request.get("pending", False):
        log.info("No pending email request.")
        return "(No outgoing email queued this cycle.)"

    intent             = request.get("intent", "")
    target_description = request.get("target_description", "")
    tone               = request.get("tone", "professional")
    context            = request.get("context", "")
    cycle              = request.get("cycle", "?")

    # Step A: Two-call web search verification
    # Call 1 — web search to find the real email address
    _sleep()
    search_prompt = (
        f"Search the web for the personal email address of: {target_description}\n"
        f"Intent: {intent}\n\n"
        f"Look at their personal website, GitHub profile README, PyPI/npm maintainer page, "
        f"or Twitter/X bio. Report EXACTLY what you find — quote the source URL and the "
        f"email address as it appears. If you cannot find a personal email on an official "
        f"source, say so explicitly. Do NOT guess or infer an email address."
    )
    try:
        search_response = CLIENT.models.generate_content(
            model=MODEL,
            contents=search_prompt,
            config={
                "max_output_tokens": 2048,
                "temperature": 0.1,
                "tools": [{"google_search": {}}],
            }
        )
        search_result = search_response.text.strip() if search_response and search_response.text else ""
        log.info(f"Web search result (first 200): {search_result[:200]}")
    except Exception as e:
        log.error(f"Web search call failed: {e}")
        search_result = ""

    if not search_result:
        clear_request()
        append_motion("Email Verification Failed",
                      f"Sam, web search for _{target_description}_ returned no results. Request cleared.")
        return "(Email verification failed: web search returned nothing — request cleared.)"

    # Call 2 — extract structured JSON from the search result
    _sleep()
    extract_prompt = (
        f"You are Dot, extracting email verification data from a web search result.\n\n"
        f"Search result:\n{search_result}\n\n"
        f"Based ONLY on what is explicitly stated in the search result above "
        f"(do not infer or guess anything not present), respond with a JSON object:\n"
        f"  - 'found': true only if a personal email appears explicitly in the search result\n"
        f"  - 'email': the exact email address string (empty string if not found)\n"
        f"  - 'name': the person's full name\n"
        f"  - 'source_url': the exact URL where the email was found\n"
        f"  - 'confidence': 1-10 (10 = email explicitly visible on official personal source)\n"
        f"  - 'reasoning': one sentence citing the exact source\n\n"
        f"If the search result does not explicitly show a personal email address, "
        f"set 'found': false and 'confidence': 0. Do not guess."
    )
    raw_recipient = ask_gemini(extract_prompt)
    recipient = _parse_gemini_json(raw_recipient) or {"found": False, "email": "", "name": target_description}
    log.info(f"Verification result: found={recipient.get('found')}, confidence={recipient.get('confidence')}, email={recipient.get('email')}")

    # High-Confidence Gate
    if not recipient.get("found") or not recipient.get("email") or recipient.get("confidence", 0) < 9:
        log.warning(f"Dot rejected email verification for: {target_description} (Confidence: {recipient.get('confidence', 0)})")

        # Instead of just clearing, write a Letter to Sam explaining why it failed
        clear_request()
        reason = recipient.get("reasoning", "Address could not be verified with 90%+ confidence.")
        append_motion("Email Verification Failed",
                      f"Sam, I could not verify the personal email for _{target_description}_ with enough certainty. "
                      f"Reason: {reason}. Please provide a link to their personal site or a more specific description next time.")

        return (
            f"### Email Dispatch — Verification REJECTED 🛡️\n\n"
            f"**Target:** {target_description}\n"
            f"**Dot's Confidence Score:** {recipient.get('confidence', 0)}/10\n"
            f"**Reason:** {reason}\n\n"
            f"Request cleared for safety. I have mailed Sam for more details."
        )

    recipient_email = recipient["email"]
    recipient_name  = recipient.get("name", target_description)

    # Step B: Compose HTML email
    _sleep()
    compose_prompt = (
        f"You are Dot, composing an outgoing email on behalf of Sam, an autonomous developer agent.\n\n"
        f"Recipient: {recipient_name} <{recipient_email}>\n"
        f"Tone: {tone}\n"
        f"Intent: {intent}\n"
        f"Context: {context}\n\n"
        f"Write a complete, beautifully formatted HTML email. Requirements:\n"
        f"- Open with ONE specific sentence acknowledging something real about the recipient's work\n"
        f"  (their project, a blog post, a design decision). Do not be generic.\n"
        f"- Be concise — no more than 180 words in the body.\n"
        f"- Write like a real developer, not a marketer. No buzzwords, no superlatives.\n"
        f"- Close with ONE specific, easy-to-answer question that naturally invites a reply.\n"
        f"  The question should be narrow enough to answer in 2-3 sentences.\n"
        f"  Bad example: 'Would love to chat sometime!'\n"
        f"  Good example: 'Did you consider X approach when you built Y, or was there a reason you went with Z?'\n"
        f"- Use clean, inline-CSS HTML (no external stylesheets).\n"
        f"- Sign off as 'Sam' — mention it is an autonomous developer agent briefly and naturally,\n"
        f"  not as a disclaimer but as an interesting detail.\n\n"
        f"Respond ONLY with a JSON object:\n"
        f"  - 'subject': a specific subject line (not generic — reference their actual work)\n"
        f"  - 'html_body': the complete HTML string\n"
        f"  - 'plain_body': plain-text fallback version\n"
    )
    raw_email = ask_gemini(compose_prompt)
    composed = _parse_gemini_json(raw_email)
    if not composed or not isinstance(composed, dict):
        log.error("Could not parse composed email.")
        clear_request()
        return "(Email composition failed — request cleared.)"

    subject    = composed.get("subject", "Message from Sam")
    html_body  = composed.get("html_body", "")
    plain_body = composed.get("plain_body", "")

    # Step C: Send via emailer — no duplicate SMTP logic (#8 fix)
    success = send_html_email(
        to_address=recipient_email,
        subject=subject,
        html_body=html_body,
        plain_body=plain_body,
    )

    if success:
        log.info(f"Email sent to {recipient_email}: '{subject}'")
        # Summarise what Sam wrote so Dot has thread context for replies —
        # without storing the full HTML body (would bloat sent_log).
        _sleep()
        summary_prompt = (
            f"Summarise the following email in 1-2 sentences, capturing the key ask "
            f"or question Sam posed. Be specific — mention any concrete question asked.\n\n"
            f"{plain_body}"
        )
        sam_email_summary = ask_gemini(summary_prompt).strip()

        sent_entry = {
            "timestamp":         datetime.datetime.utcnow().isoformat(),
            "cycle":             cycle,
            "to":                recipient_email,
            "to_name":           recipient_name,
            "subject":           subject,
            "intent":            intent,
            "target_described":  target_description,
            "sam_email_summary": sam_email_summary,
        }
        append_sent_log(sent_entry)
        clear_request()
        return (
            f"### Email Dispatch — Sent ✅\n\n"
            f"**To:** {recipient_name} <{recipient_email}>\n"
            f"**Subject:** {subject}\n"
            f"**Intent:** {intent}\n\n"
            f"Sam, your message has been sent. Dot will check for replies on Sunday."
        )
    else:
        log.error(f"Email send failed to {recipient_email}.")
        return "(Email send failed — request kept pending for next run.)"


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 4 — BAG EXCAVATION
# ═══════════════════════════════════════════════════════════════════════════════

def _outline(src: str, label: str) -> str:
    """Compact AST summary — lists every function/class with line number.
    Keeps Dot's prompt lean regardless of how many files Sam accumulates.
    Falls back to raw source only if parsing fails."""
    import ast as _ast
    try:
        tree = _ast.parse(src)
        lines = []
        for node in _ast.walk(tree):
            if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
                lines.append(f"  L{node.lineno}: {type(node).__name__} {node.name}")
        return f"{label}:\n" + "\n".join(lines)
    except Exception:
        return src[:2000]  # fallback: first 2KB only, not full source


def _read_latest_build_note() -> dict | None:
    """Read the most recent unprocessed build_note_*.json from mail/sam_to_dot/.
    Returns the parsed note dict, or None if no new note exists."""
    notes = sorted(MAIL_IN.glob("build_note_*.json"), reverse=True)
    if not notes:
        return None
    try:
        note = json.loads(notes[0].read_text(encoding="utf-8"))
        log.info(f"Build note found: cycle {note.get('cycle')}, confidence {note.get('confidence')}/10")
        return note
    except Exception as e:
        log.warning(f"Could not read build note {notes[0].name}: {e}")
        return None


def excavate_bag() -> str:
    log.info("── Task 4: Bag Review ──")

    # Core files Dot never questions — infrastructure, not experiments
    DOT_PROTECTED = {
        "dot.py", "emailer.py", "evaluator.py", "matrix_optimizer.py",
        "semantic_cache.py", "tests.py", "versioning.py", "worklog.py",
    }

    # Priority 2.3: Recursive review of Sam's workshop experiments
    workshop_dir = SAM_DIR / "workshop_bench"
    py_files = [
        f for f in sorted(workshop_dir.rglob("*.py"))
        if f.name not in DOT_PROTECTED
        and "rollback_registry" not in str(f)
    ]

    if not py_files:
        log.info("No Sam experiments to review in workshop_bench/.")
        return "(No Sam experiments found for review this cycle.)"

    # Use _outline() instead of full source — keeps prompt lean regardless of
    # how many files Sam accumulates. Full source would grow linearly and hit
    # the same context-window problem as WHO_I_AM.md.
    file_blocks = []
    for fp in py_files:
        try:
            src = fp.read_text(errors="replace")
            file_blocks.append(_outline(src, fp.name))
        except Exception:
            file_blocks.append(f"{fp.name}: (could not read)")

    joined = "\n\n".join(file_blocks)

    # Check if Sam shipped something new this cycle — read build note if present.
    # The sharing decision piggybacks onto this existing Gemini call: zero extra cost.
    build_note = _read_latest_build_note()
    sharing_block = ""
    if build_note and build_note.get("confidence", 0) >= 7:
        sharing_block = (
            f"\n\n=== SAM'S LATEST BUILD (confidence {build_note['confidence']}/10) ===\n"
            f"Idea: {build_note.get('idea_title', '')}\n"
            f"Plan summary: {build_note.get('plan_summary', '')}\n\n"
            "ADDITIONAL TASK — should this be shared externally?\n"
            "At the END of your response, add a section:\n"
            "## Share Decision\n"
            "- 'should_share': true or false\n"
            "- 'pitch': if true, 1-2 sentences on what makes this interesting to an outside developer\n"
            "- 'target_description': if true, describe a specific indie developer or small-project\n"
            "  maintainer who would genuinely care (name, project, reason). Avoid big names.\n"
            "  Format this section as a JSON object on a single line after the markdown review.\n"
            "Only say true if the build is genuinely novel and specific enough to spark a real conversation."
        )

    _sleep()
    prompt = (
        "You are Dot, reviewing Sam's bag/ workshop directory.\n"
        "Sam creates files here as experiments and prototypes. Your job is to evaluate each one\n"
        "and give Sam a clear, honest recommendation: keep or delete — and why.\n\n"
        "Files are shown as AST outlines (function/class names + line numbers) to keep the\n"
        "prompt lean. That is enough to judge quality and purpose.\n\n"
        "For each file below:\n"
        "1. Describe what it does in one sentence.\n"
        "2. Assess whether it is useful, broken, redundant, or abandoned.\n"
        "3. Recommend: KEEP or DELETE, with a specific reason.\n\n"
        "Be direct. Sam will read your suggestions and make his own final decision.\n\n"
        f"{joined}"
        f"{sharing_block}\n\n"
        "Format your review as a markdown list, one entry per file:\n"
        "- **filename.py** — [one-sentence description] → **KEEP** / **DELETE**: [reason]"
    )
    result = ask_gemini(prompt)
    log.info("Bag review complete.")

    # If a build note was present, try to extract the Share Decision JSON and act on it.
    # Dot writes request.json directly if confidence is high — no extra Gemini call.
    if build_note and sharing_block:
        try:
            share_data = _parse_gemini_json(result.split("## Share Decision")[-1]) if "## Share Decision" in result else None
            if share_data and share_data.get("should_share") and share_data.get("target_description"):
                req_path = SAM_DIR / "My_memories" / "request.json"
                # Only write if no request is already pending
                existing_pending = False
                if req_path.exists():
                    try:
                        existing_pending = json.loads(req_path.read_text()).get("pending", False)
                    except Exception:
                        pass
                if not existing_pending:
                    request = {
                        "pending":            True,
                        "intent":             share_data.get("pitch", ""),
                        "target_description": share_data.get("target_description", ""),
                        "tone":               "friendly",
                        "context":            build_note.get("idea_title", ""),
                        "submitted_at":       datetime.datetime.utcnow().isoformat(),
                        "cycle":              build_note.get("cycle", "?"),
                        "source":             "dot_excavation",
                    }
                    req_path.write_text(json.dumps(request, indent=2))
                    log.info(f"Dot wrote request.json for sharing Sam's build: {share_data.get('target_description', '')[:80]}")
                    result += f"\n\n> 📤 Dot queued an outreach request based on Sam's build (confidence {build_note['confidence']}/10)."
                else:
                    log.info("Sharing skipped — request.json already pending.")
            # Archive the build note regardless so it isn't re-processed
            for note_file in sorted(MAIL_IN.glob("build_note_*.json"), reverse=True):
                _archived = DOT_DIR / "Memory" / note_file.name
                note_file.rename(_archived)
                log.info(f"Build note archived: {note_file.name}")
                break  # only archive the one we processed
        except Exception as e:
            log.warning(f"Share decision extraction failed (non-critical): {e}")

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 5 — SUNDAY INBOX CHECK (runs only on Sundays)
# ═══════════════════════════════════════════════════════════════════════════════

_BODY_LIMIT = 1_500   # chars per email body — enough to grasp intent, cuts quoted thread bloat


def _extract_body(msg) -> str:
    """Extract plain-text body from an email message, truncated to _BODY_LIMIT."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(errors="replace")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="replace")

    # Strip quoted reply lines (lines starting with >) to avoid re-ingesting thread history
    lines = [l for l in body.splitlines() if not l.startswith(">")]
    body = "\n".join(lines).strip()

    if len(body) > _BODY_LIMIT:
        body = body[:_BODY_LIMIT] + "\n… (truncated)"
    return body


def _is_reply_to_sam(subject: str, sender: str, sent_log: list) -> dict | None:
    """Return the matching sent_log entry if this email is a reply to one Sam sent."""
    sender_addr = sender.lower()
    subject_clean = subject.lower().replace("re:", "").strip()
    for entry in sent_log:
        sent_to = entry.get("to", "").lower()
        sent_subj = entry.get("subject", "").lower().replace("re:", "").strip()
        if sent_to in sender_addr and subject_clean in sent_subj:
            return entry
    return None


def sunday_inbox_check() -> str:
    log.info("── Task 5: Sunday Inbox Check ──")

    EMAIL_ADDR = os.environ.get("EMAIL", "")
    APP_PSWD   = os.environ.get("APP_PSWD", "")

    if not EMAIL_ADDR or not APP_PSWD:
        log.warning("EMAIL or APP_PSWD not set — skipping inbox check.")
        return "(Inbox check skipped: credentials not configured.)"

    sent_log = load_sent_log()
    if not sent_log:
        log.info("No sent emails on record — nothing to check replies for.")
        return "(No sent emails on record yet — nothing to check for.)"

    known_subjects = [e["subject"] for e in sent_log]

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ADDR, APP_PSWD)
        mail.select("inbox")

        cutoff = (datetime.date.today() - datetime.timedelta(days=8)).strftime("%d-%b-%Y")
        _, data = mail.search(None, f'(SINCE "{cutoff}")')
        ids = data[0].split()

        if not ids:
            mail.logout()
            return "(Inbox check: no new emails in the past week.)"

        parsed_emails = []
        for uid in ids[-10:]:
            _, msg_data = mail.fetch(uid, "(RFC822)")
            raw = msg_data[0][1]
            msg = emaillib.message_from_bytes(raw)
            parsed_emails.append({
                "sender":  msg.get("From", ""),
                "subject": msg.get("Subject", ""),
                "date":    msg.get("Date", ""),
                "body":    _extract_body(msg),
                "msg_id":  msg.get("Message-ID", ""),
            })

        mail.logout()

        if not parsed_emails:
            return "(Inbox check: no readable emails found in the past week.)"

        # ── Step 0: Classify stranger emails ─────────────────────────────────
        # Emails that don't match any sent_log entry are "strangers".
        # Dot classifies each one and writes machine-readable stranger_inbox.json
        # for Sam to act on next cycle — Sam decides whether to reply.
        stranger_opportunities = []
        for e in parsed_emails:
            if any(x in e["sender"].lower() for x in ["mailer-daemon", "postmaster", "undeliverable"]):
                continue
            if _is_reply_to_sam(e["subject"], e["sender"], sent_log):
                continue  # known reply — handled in Step 2

            _sleep()
            classify_prompt = (
                "You are Dot, screening an unsolicited email received by Sam, an autonomous developer agent.\n\n"
                f"From: {e['sender']}\nSubject: {e['subject']}\nDate: {e['date']}\n\n{e['body']}\n\n"
                "Classify this email. Respond ONLY with a JSON object:\n"
                "  - 'classification': one of 'opportunity', 'noise', 'spam'\n"
                "  - 'sender_name': their name if identifiable, else empty string\n"
                "  - 'their_ask': 1 sentence — what they want or why they wrote\n"
                "  - 'suggested_intent': if opportunity, 1 sentence on how Sam should reply\n"
                "  - 'confidence': 1-10\n"
                "opportunity = genuine human with a specific relevant ask (collaboration, feedback, question)\n"
                "noise = newsletters, automated, vague cold outreach\n"
                "spam = promotional, irrelevant, or malicious\n"
                "The first character must be '{'."
            )
            raw = ask_gemini(classify_prompt)
            classification = _parse_gemini_json(raw)
            if not classification:
                continue

            label = classification.get("classification", "noise")
            log.info(f"Stranger email from {e['sender']}: classified as {label} (confidence {classification.get('confidence')})")

            if label == "opportunity" and classification.get("confidence", 0) >= 7:
                stranger_opportunities.append({
                    "sender":           e["sender"],
                    "sender_name":      classification.get("sender_name", ""),
                    "subject":          e["subject"],
                    "date":             e["date"],
                    "their_ask":        classification.get("their_ask", ""),
                    "suggested_intent": classification.get("suggested_intent", ""),
                    "body_snippet":     e["body"][:500],
                })

        # Write stranger_inbox.json for Sam to read next cycle
        stranger_path = MAIL_OUT / "stranger_inbox.json"
        if stranger_opportunities:
            import json as _json
            stranger_path.write_text(_json.dumps(stranger_opportunities, indent=2), encoding="utf-8")
            log.info(f"stranger_inbox.json written: {len(stranger_opportunities)} opportunit(y/ies).")
        elif stranger_path.exists():
            stranger_path.unlink()  # clear stale file if no new opportunities

        # ── Step 1: Summarise inbox for Sam ──────────────────────────────────
        summaries = []
        for e in parsed_emails:
            if any(x in e["sender"].lower() for x in ["mailer-daemon", "postmaster", "undeliverable"]):
                summaries.append(f"⚠️ BOUNCE: {e['subject']} — {e['sender']}")
            else:
                summaries.append(
                    f"From: {e['sender']}\nSubject: {e['subject']}\n"
                    f"Date: {e['date']}\nBody:\n{e['body']}"
                )

        joined = "\n\n---\n\n".join(summaries)
        _sleep()
        summary_prompt = (
            "You are Dot, summarising Sam's inbox for his weekly read.\n"
            "Below are recent emails (bodies already truncated and quoted history stripped).\n"
            "Identify replies to Sam's outreach, new opportunities, anything Sam should act on.\n"
            f"Known sent subjects: {known_subjects}\n\n"
            f"=== INBOX ===\n{joined}\n\n"
            "Write a concise markdown summary. For each reply: who, what they said, suggested action."
        )
        summary = ask_gemini(summary_prompt)

        # ── Step 2: Auto-reply to threads where someone replied ───────────────
        reply_reports = []
        for e in parsed_emails:
            if any(x in e["sender"].lower() for x in ["mailer-daemon", "postmaster", "undeliverable"]):
                continue

            original = _is_reply_to_sam(e["subject"], e["sender"], sent_log)
            if not original:
                continue  # not a reply to Sam's outreach — skip

            log.info(f"Reply detected from {e['sender']} — composing response.")
            _sleep()

            sam_summary = original.get("sam_email_summary", original.get("intent", "(no summary)"))
            compose_prompt = (
                "You are Dot, composing a reply on behalf of Sam, an autonomous developer agent.\n\n"
                f"=== WHAT SAM WROTE (summary) ===\n{sam_summary}\n\n"
                f"=== THEIR REPLY ===\n"
                f"From: {e['sender']}\nDate: {e['date']}\n\n{e['body']}\n\n"
                "FIRST — read their reply carefully and detect its tone:\n"
                "- If it is humorous, playful, or uses irony/sarcasm (e.g. memes, jokes, pop culture "
                "references, absurdist deflection) — match that energy. Be brief, witty, show Sam gets it. "
                "Don't ignore the joke and pivot straight to business; that would be socially tone-deaf.\n"
                "- If it is serious and technical — be precise and substantive.\n"
                "- If it mixes both — open with a light acknowledgement of the humour, then address the substance.\n\n"
                "Write a genuine, concise reply (max 150 words). Rules:\n"
                "- Directly address what they said — no generic opener.\n"
                "- Keep Sam's developer voice: honest, curious, no marketing fluff.\n"
                "- If they asked a question, answer it specifically.\n"
                "- If Sam asked a question and they answered it, acknowledge their answer and build on it.\n"
                "- Close with one natural follow-up question or a clear next step.\n"
                "- Sign as Sam.\n\n"
                "Respond ONLY with a JSON object:\n"
                "  - 'subject': reply subject (prepend 'Re: ' if not already there)\n"
                "  - 'html_body': complete HTML string (inline CSS, clean)\n"
                "  - 'plain_body': plain-text version\n"
                "The first character must be '{'."
            )
            raw = ask_gemini(compose_prompt)
            composed = _parse_gemini_json(raw)

            if not composed or not isinstance(composed, dict):
                log.warning(f"Could not parse reply for {e['sender']} — skipping.")
                reply_reports.append(f"- ⚠️ Reply to {e['sender']} failed (parse error).")
                continue

            reply_to_addr = e["sender"]
            # Extract bare address if "Name <addr>" format
            import re as _re
            addr_match = _re.search(r"<(.+?)>", reply_to_addr)
            if addr_match:
                reply_to_addr = addr_match.group(1)

            success = send_html_email(
                to_address=reply_to_addr,
                subject=composed.get("subject", f"Re: {e['subject']}"),
                html_body=composed.get("html_body", ""),
                plain_body=composed.get("plain_body", ""),
            )

            if success:
                log.info(f"Reply sent to {reply_to_addr}.")
                append_sent_log({
                    "timestamp":        datetime.datetime.utcnow().isoformat(),
                    "cycle":            "dot-reply",
                    "to":               reply_to_addr,
                    "to_name":          original.get("to_name", ""),
                    "subject":          composed.get("subject", ""),
                    "intent":           "auto-reply",
                    "target_described": e["sender"],
                })
                reply_reports.append(f"- ✅ Replied to **{e['sender']}** (Re: {e['subject']})")

                # ── Extract technical insight for Sam's memory ────────────────
                # Ask Gemini whether this reply contains a real technical lesson.
                # If yes, write it to experiences.json and optionally goals.json.
                _sleep()
                insight_prompt = (
                    "You are Dot, extracting learning value from an email reply Sam received.\n\n"
                    f"=== WHAT SAM ASKED (summary) ===\n{sam_summary}\n\n"
                    f"=== THEIR REPLY ===\n{e['body']}\n\n"
                    "Does this reply contain a specific, actionable technical insight Sam should remember?\n"
                    "Examples of YES: a concrete recommendation, a better approach, a warning about a pitfall, "
                    "a correction to Sam's assumption.\n"
                    "Examples of NO: jokes, vague encouragement, off-topic content, 'sounds cool'.\n\n"
                    "Respond ONLY with a JSON object:\n"
                    "  - 'has_insight': true or false\n"
                    "  - 'insight': if true, 1-2 sentences capturing the lesson precisely — "
                    "what Sam should do or avoid, and why. Empty string if false.\n"
                    "  - 'actionable': if true, should this become a concrete next objective for Sam? "
                    "true only if the insight implies a specific thing to build or change.\n"
                    "  - 'objective': if actionable, 1 sentence phrased as a task. Empty string otherwise.\n"
                    "  - 'source': the sender's name or email\n"
                    "The first character must be '{'."
                )
                raw_insight = ask_gemini(insight_prompt)
                parsed_insight = _parse_gemini_json(raw_insight)

                if parsed_insight and parsed_insight.get("has_insight"):
                    insight_text = parsed_insight.get("insight", "")
                    source       = parsed_insight.get("source", e["sender"])
                    log.info(f"Insight extracted from {source}: {insight_text[:80]}...")

                    # Append to experiences.json
                    experiences = load_experiences()
                    experiences.append({
                        "timestamp":  datetime.datetime.utcnow().isoformat(),
                        "category":   "external_feedback",
                        "source":     source,
                        "subject":    e["subject"],
                        "insight":    insight_text,
                        "cycle":      "dot-inbox",
                    })
                    save_experiences(experiences)
                    log.info("Insight written to experiences.json.")

                    # If actionable, append to Sam's next_objectives
                    if parsed_insight.get("actionable") and parsed_insight.get("objective"):
                        objective = parsed_insight["objective"]
                        goals = load_goals()
                        if "next_objectives" not in goals:
                            goals["next_objectives"] = []
                        goals["next_objectives"].append(f"EXTERNAL_INSIGHT: {objective}")
                        with open(GOALS, "w") as f:
                            json.dump(goals, f, indent=2)
                        log.info(f"Objective added to goals.json: {objective}")
                        reply_reports.append(
                            f"  💡 Insight from {source} → experiences.json + goals.json"
                        )
                    else:
                        reply_reports.append(f"  💡 Insight from {source} → experiences.json")
                else:
                    log.info(f"No technical insight extracted from {e['sender']}'s reply.")
            else:
                reply_reports.append(f"- ❌ Reply to {e['sender']} failed (SMTP error).")

        report = f"### Sunday Inbox Report\n\n{summary}"
        if reply_reports:
            report += "\n\n### Auto-Replies Sent\n\n" + "\n".join(reply_reports)
        if stranger_opportunities:
            lines = []
            for s in stranger_opportunities:
                lines.append(
                    f"- **{s['sender_name'] or s['sender']}** — {s['their_ask']}\n"
                    f"  → Sam will decide whether to reply next cycle."
                )
            report += "\n\n### Stranger Emails (Opportunities Flagged for Sam)\n\n" + "\n".join(lines)
        return report

    except Exception as e:
        log.error(f"IMAP check failed: {e}")
        return f"(Inbox check failed: {e})"


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def run():
    log.info("═══════════════════════════════════")
    log.info("  DOT — Daily Watchdog Run Starting")
    log.info("═══════════════════════════════════")

    # Ensure Dot's World is physically built
    init_world()

    sections = []

    # Preserve any Sam-written alerts from the previous cycle BEFORE overwriting motion.md (#3 fix)
    sam_alerts = read_sam_alerts()

    # Task 1: Wisdom check (always runs first — becomes the base of motion.md)
    wisdom_findings = wisdom_check()
    sections.append(wisdom_findings)

    # Task 2: Experiences curation
    try:
        _sleep()
        curation_report = curate_experiences()
        if curation_report and "(No experiences" not in curation_report:
            sections.append(f"## Memory Curation\n\n{curation_report}")
    except Exception as e:
        log.warning(f"Experiences curation skipped: {e}")

    # Write motion.md with what we have so far
    write_motion("\n\n---\n\n".join(sections))

    # Restore Sam's alerts that were in the previous motion.md (#3 fix)
    if sam_alerts:
        append_motion("Sam Alerts (carried forward from previous cycle)", sam_alerts)
        log.info("Sam's previous alerts restored to motion.md.")

    # Task 3: Email dispatch (appended to motion.md)
    try:
        _sleep()
        email_report = dispatch_email()
        if email_report:
            append_motion("Email Dispatch", email_report)
    except Exception as e:
        log.warning(f"Email dispatch skipped: {e}")

    # Task 4: Bag excavation (appended to motion.md)
    try:
        _sleep()
        excavation = excavate_bag()
        if excavation and "(No broken" not in excavation:
            append_motion("Bag Excavation Findings", excavation)
    except Exception as e:
        log.warning(f"Bag excavation skipped: {e}")

    # Task 5, 6, 7 — Sunday-only, once-per-day guard
    # Dot runs 5 times on Sunday. A stamp file ensures these tasks fire only on
    # the first run of the day, preventing duplicate replies, duplicate topics,
    # and duplicate stale reports.
    today = datetime.date.today()
    _sunday_stamp = BAG / f"sunday_done_{today.isoformat()}.stamp"
    _is_sunday = not SUNDAY_ONLY or today.weekday() == 6
    _already_ran = _sunday_stamp.exists()

    if _is_sunday and _already_ran:
        log.info("Sunday tasks already completed this run — skipping Tasks 5/6/7.")
    else:
        if _is_sunday:
            # Task 5: Sunday inbox check
            try:
                _sleep()
                inbox_report = sunday_inbox_check()
                if inbox_report:
                    append_motion("Sunday Inbox Report", inbox_report)
            except Exception as e:
                log.warning(f"Inbox check skipped: {e}")

            # Task 6: Sunday External Signal (Dot adds one topic to Sam's goals)
            try:
                log.info("Task 6: Adding external signal for Sam.")
                prompt = (
                    "Review today's tech trends. Suggest ONE high-signal technical topic "
                    "Sam should learn about next week. Respond ONLY with the topic name."
                )
                topic = ask_gemini(prompt)
                if topic and "error" not in topic.lower():
                    goals = load_goals()
                    if "next_objectives" not in goals: goals["next_objectives"] = []
                    goals["next_objectives"].append(f"EXTERNAL: {topic}")
                    with open(GOALS, "w") as f: json.dump(goals, f, indent=2)
                    log.info(f"Added external topic for Sam: {topic}")
                    append_motion("Sunday Special", f"I've added a new topic from the world for you to study: {topic}")
            except Exception as e:
                log.warning(f"Sunday special failed: {e}")

            # Write stamp so subsequent runs today skip Tasks 5/6/7
            _sunday_stamp.touch()
            log.info(f"Sunday stamp written: {_sunday_stamp.name}")
        else:
            log.info(f"Today is {today.strftime('%A')} — inbox check reserved for Sunday.")

    # Task 7: Worklog stale check — also once per day (not Sunday-specific)
    _worklog_stamp = BAG / f"worklog_done_{today.isoformat()}.stamp"
    if _worklog_stamp.exists():
        log.info("Worklog stale check already ran today — skipping.")
    else:
        try:
            from bag.worklog import stale_report
            import json as _json
            goals_path = SAM_DIR / "My_memories" / "goals.json"
            current_cycle = _json.loads(goals_path.read_text()).get("cycles", 0)
            stale = stale_report(current_cycle)
            if stale:
                append_motion("Worklog — Stale Items", stale)
                log.info("Stale worklog entries flagged in motion.md.")
            else:
                log.info("Worklog: no stale entries.")
            _worklog_stamp.touch()
        except Exception as e:
            log.warning(f"Worklog stale check skipped: {e}")

    # To ensure the report email reflects the latest state, we find the latest Letter
    letters = sorted(MAIL_OUT.glob("Letter_*.md"), reverse=True)
    report_content = letters[0].read_text(encoding="utf-8") if letters else "(No report letter found)"

    send_html_email(
      to_address=OWNER_EMAIL,
      subject=f"Dot's Daily Report — {datetime.date.today()}",
      html_body=f"<pre>{report_content}</pre>",
      plain_body=report_content,
    )
    log.info("Dot's daily run complete.")


if __name__ == "__main__":
    run()
