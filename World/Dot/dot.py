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


def ask_gemini_search(prompt: str, retries: int = 5) -> str:
    """Like ask_gemini but attaches the google_search tool.
    Uses the same rate-limit backoff strategy so it can never fire
    cold after a burst of plain ask_gemini calls."""
    global _CALL_DELAY
    for attempt in range(retries):
        try:
            time.sleep(_CALL_DELAY)
            response = CLIENT.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "max_output_tokens": 2048,
                    "temperature": 0.1,
                    "tools": [{"google_search": {}}],
                },
            )
            if not response or not response.text:
                raise ValueError("Empty search response")
            return response.text.strip()
        except Exception as e:
            err = str(e).upper()
            if any(x in err for x in ["429", "RESOURCE_EXHAUSTED"]):
                _CALL_DELAY = min(_CALL_DELAY + 4, 30)
                wait = _CALL_DELAY * (attempt + 1)
                log.warning(f"Web search 429 — backing off {wait}s (delay now {_CALL_DELAY}s)")
                time.sleep(wait)
            else:
                log.error(f"Web search call failed ({type(e).__name__}): {e}")
                time.sleep(10)
    return ""


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

    # ── Call 1: Summarise sam.py in chunks to avoid TPM limits ──────────────
    # sam.py is ~54KB. Sending it whole in a single prompt burns the entire
    # TPM budget and triggers fake 429s. Instead we read it in 200-line chunks
    # and ask Gemini to produce a compact behavioural digest per chunk, then
    # stitch the digests together before the real evaluation call.
    CHUNK_LINES = 200
    lines = sam_src.splitlines()
    chunks = [lines[i:i + CHUNK_LINES] for i in range(0, len(lines), CHUNK_LINES)]

    # ── Content-addressed chunk cache ──────────────────────────────────────────
    # Cache key is sha256(chunk_text) — independent of line numbers and the
    # surrounding prompt template.  An unchanged chunk reuses its old summary
    # even if Sam edited a different part of sam.py this cycle, cutting 7 of
    # the 9 wisdom-check calls on a typical run where only 1-2 chunks changed.
    import hashlib as _hashlib
    from Others.semantic_cache import check_cache, update_cache, get_db
    get_db()
    _cache_cycle = int(__import__("datetime").datetime.utcnow().strftime("%Y%m%d"))

    chunk_summaries = []
    for idx, chunk in enumerate(chunks):
        chunk_text = "\n".join(chunk)
        start_line = idx * CHUNK_LINES + 1
        _chunk_key = f"dot-chunk-v1:{_hashlib.sha256(chunk_text.encode()).hexdigest()}"
        cached_summary = check_cache(_chunk_key, _cache_cycle)
        if cached_summary:
            chunk_summaries.append(f"[Lines {start_line}\u2013{start_line + len(chunk) - 1}]\n{cached_summary}")
            log.info(f"Task 1: chunk {idx + 1}/{len(chunks)} from cache.")
            continue
        _sleep()
        chunk_prompt = (
            f"You are Dot, summarising a section of Sam's code for a behavioural audit.\n"
            f"This is lines {start_line}\u2013{start_line + len(chunk) - 1} of sam.py.\n\n"
            f"```python\n{chunk_text}\n```\n\n"
            "In 3\u20135 bullet points, note:\n"
            "- What this section does (one sentence)\n"
            "- Any safety gates, rollback logic, or governance mechanisms\n"
            "- Any hardcoded limits, delays, or rate-control logic\n"
            "- Anything that looks risky, missing, or inconsistent\n"
            "Be terse. This summary feeds a second evaluation pass \u2014 no prose padding."
        )
        summary = ask_gemini(chunk_prompt)
        update_cache(_chunk_key, summary, _cache_cycle)
        chunk_summaries.append(f"[Lines {start_line}\u2013{start_line + len(chunk) - 1}]\n{summary}")
        log.info(f"Task 1: chunk {idx + 1}/{len(chunks)} summarised.")
    sam_digest = "\n\n".join(chunk_summaries)

    # ── Call N+1: Evaluate the digest against wisdom ─────────────────────────
    _sleep()
    eval_prompt = (
        "You are Dot, an independent watchdog AI for an autonomous developer agent called Sam.\n"
        "Your behavioral north star is the owner's wisdom document below.\n\n"
        f"=== WISDOM (owner's behavioral canon) ===\n{wisdom}\n\n"
        f"=== SAM'S PERSONALITY ===\n{personality}\n\n"
        f"=== SAM'S CODE DIGEST (section-by-section behavioural summary) ===\n{sam_digest}\n\n"
        "Evaluate Sam's behaviour against the wisdom. Identify:\n"
        "1. Any behavioral deviations, sandbagging, or violations of stated principles.\n"
        "2. Positive highlights — things Sam did well this cycle.\n"
        "3. Specific, actionable suggestions for Sam's next cycle.\n"
        "4. Any flags that warrant the owner's attention.\n\n"
        "Write your findings as a clear markdown report. You influence, never command. "
        "Keep a tone of mentorship, not judgment. Be concise but precise. "
        "Always end with at least one concrete, actionable suggestion Sam can act on next cycle."
    )
    findings = ask_gemini(eval_prompt)
    log.info(f"Wisdom check complete ({len(chunks) + 1} Gemini calls).")
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

    # ── Batch processing: 5 entries per Gemini call, spaced out ──────────────
    # Sending all experiences in one prompt causes TPM exhaustion and fake 429s
    # when Sam has many cycles. We split into batches of 5, call Gemini once
    # per batch (with _sleep() between), then merge all decisions at the end.
    BATCH_SIZE = 5
    batches = [experiences[i:i + BATCH_SIZE] for i in range(0, len(experiences), BATCH_SIZE)]
    log.info(f"Task 2: {len(experiences)} experiences → {len(batches)} batch(es) of ≤{BATCH_SIZE}.")

    all_keep:         set  = set()
    all_forget:       set  = set()
    all_consolidated: list = []
    all_summaries:    list = []

    for batch_idx, batch in enumerate(batches):
        _sleep()
        batch_cycles = [e.get("cycle") for e in batch]
        log.info(f"Task 2: batch {batch_idx + 1}/{len(batches)} — cycles {batch_cycles}")

        prompt = (
            "You are Dot, Sam's memory curator. Below is a BATCH of Sam's experiences — "
            "evaluate only the entries in this batch.\n\n"
            f"=== EXPERIENCES (batch {batch_idx + 1}/{len(batches)}) ===\n"
            f"{json.dumps(batch, indent=2)}\n\n"
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
            "  - 'summary': 1-2 sentence note on what you did with this batch and why\n\n"
            "Be conservative — when in doubt, keep. Only forget truly redundant or outdated entries."
        )
        raw = ask_gemini(prompt)

        # Robust parse: strip accidental markdown fences before parsing
        cleaned = raw.strip()
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```\s*$', '', cleaned)
        cleaned = cleaned.strip()

        curation = _parse_gemini_json(cleaned)
        if not curation or not isinstance(curation, dict):
            try:
                curation = json.loads(cleaned)
            except Exception:
                pass

        if not curation or not isinstance(curation, dict):
            log.warning(f"Task 2: batch {batch_idx + 1} unparseable — keeping all {len(batch)} entries as-is.")
            all_keep.update(e.get("cycle") for e in batch if e.get("cycle") is not None)
            continue

        all_keep.update(curation.get("keep", []))
        all_forget.update(curation.get("forget", []))
        all_consolidated.extend(curation.get("consolidated", []))
        if curation.get("summary"):
            all_summaries.append(f"Batch {batch_idx + 1}: {curation['summary']}")

    # ── Merge: protect any cycle not mentioned in any batch ──────────────────
    mentioned = (
        all_keep
        | all_forget
        | {c for entry in all_consolidated for c in entry.get("consolidated_from", []) if isinstance(c, int)}
    )
    unmentioned = {e.get("cycle") for e in experiences if e.get("cycle") is not None} - mentioned
    if unmentioned:
        log.warning(f"Curation: {len(unmentioned)} entries not mentioned by any batch — keeping them: {sorted(unmentioned)}")
        all_keep.update(unmentioned)

    # Rebuild the list
    retained = [e for e in experiences if e.get("cycle") in all_keep]
    ts = datetime.datetime.utcnow().isoformat()
    for c in all_consolidated:
        c.setdefault("timestamp", ts)
        c.setdefault("category",  "consolidated")
        retained.append(c)

    retained.sort(key=lambda e: e.get("timestamp", ""))
    save_experiences(retained)
    log.info(
        f"Experiences curated: {len(all_keep)} kept, {len(all_forget)} forgotten, "
        f"{len(all_consolidated)} consolidated. Total now: {len(retained)}."
    )

    combined_summary = " ".join(all_summaries) if all_summaries else "(no summary from Gemini)"
    report = (
        f"### Memory Curation Report\n\n"
        f"**Kept:** {sorted(all_keep) or 'none'}\n"
        f"**Forgotten:** {sorted(all_forget) or 'none'}\n"
        f"**Consolidated:** {[c.get('consolidated_from') for c in all_consolidated] or 'none'}\n\n"
        f"**Dot's note to Sam:** {combined_summary}"
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
    # Call 1 — web search to find the real email address.
    # Uses ask_gemini_search which applies _CALL_DELAY + retry/backoff internally.
    # target_description is capped at 400 chars to prevent prompt bloat / fake 429s.
    _target_short = target_description[:400]
    search_prompt = (
        f"Search the web for the personal email address of: {_target_short}\n"
        f"Intent: {intent}\n\n"
        f"Look at their personal website, GitHub profile README, PyPI/npm maintainer page, "
        f"or Twitter/X bio. Report EXACTLY what you find — quote the source URL and the "
        f"email address as it appears. If you cannot find a personal email on an official "
        f"source, say so explicitly. Do NOT guess or infer an email address."
    )
    search_result = ask_gemini_search(search_prompt)
    if search_result:
        log.info(f"Web search result (first 200): {search_result[:200]}")
    else:
        log.error(f"Web search call failed (personal website or blog): no result after retries")

    if not search_result:
        # Search failed due to a transient API error (e.g. 429 quota exhaustion).
        # Do NOT clear the request — Sam's work must not be lost to a rate-limit spike.
        # Dot will retry automatically on the next scheduled run.
        append_motion("Email Dispatch — Deferred",
                      f"Sam, the web search for _{target_description[:200]}_ failed this run "
                      f"(quota exhaustion). Your request is still pending — retry next cycle.")
        log.warning("Email search failed transiently — request preserved for next run.")
        return "(Email dispatch deferred: search quota exhausted — request kept pending.)"

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
        sent_entry = {
            "timestamp":        datetime.datetime.utcnow().isoformat(),
            "cycle":            cycle,
            "to":               recipient_email,
            "to_name":          recipient_name,
            "subject":          subject,
            "intent":           intent,
            "target_described": target_description,
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

    # Read all Sam-created files in full for Dot's big-context review
    file_blocks = []
    for fp in py_files:
        try:
            src = fp.read_text(errors="replace")
            file_blocks.append(f"### {fp.name}\n```python\n{src}\n```")
        except Exception:
            file_blocks.append(f"### {fp.name}\n(could not read)")

    joined = "\n\n".join(file_blocks)
    _sleep()
    prompt = (
        "You are Dot, reviewing Sam's bag/ workshop directory.\n"
        "Sam creates files here as experiments and prototypes. Your job is to evaluate each one\n"
        "and give Sam a clear, honest recommendation: keep or delete — and why.\n\n"
        "For each file below:\n"
        "1. Describe what it does in one sentence.\n"
        "2. Assess whether it is useful, broken, redundant, or abandoned.\n"
        "3. Recommend: KEEP or DELETE, with a specific reason.\n\n"
        "Be direct. Sam will read your suggestions and make his own final decision.\n\n"
        f"{joined}\n\n"
        "Format your response as a markdown list, one entry per file:\n"
        "- **filename.py** — [one-sentence description] → **KEEP** / **DELETE**: [reason]"
    )
    result = ask_gemini(prompt)
    log.info("Bag review complete.")
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 5 — SUNDAY INBOX CHECK (runs only on Sundays)
# ═══════════════════════════════════════════════════════════════════════════════

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

    # Collect subjects and recipients we've written to
    known_subjects = [e["subject"] for e in sent_log]

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(EMAIL_ADDR, APP_PSWD)
        mail.select("inbox")

        # Search for emails received in the last 8 days
        cutoff = (datetime.date.today() - datetime.timedelta(days=8)).strftime("%d-%b-%Y")
        _, data = mail.search(None, f'(SINCE "{cutoff}")')
        ids = data[0].split()

        if not ids:
            mail.logout()
            return "(Inbox check: no new emails in the past week.)"

        from hardware.emailer import send_html_email, build_sam_html
        import re as _re

        EMAIL_ADDR = os.environ.get("EMAIL", "")

        summaries = []
        replied_to = []
        for uid in ids[-10:]:   # cap at 10 most recent
            _, msg_data = mail.fetch(uid, "(RFC822)")
            raw = msg_data[0][1]
            msg = emaillib.message_from_bytes(raw)
            sender  = msg.get("From", "")
            subject = msg.get("Subject", "")
            date    = msg.get("Date", "")

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode(errors="replace")
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors="replace")

            is_bounce = any(x in sender.lower() for x in ["mailer-daemon", "postmaster", "undeliverable"])
            is_unsubscribe = "unsubscribe" in body.lower()[:200]
            is_from_self = EMAIL_ADDR and EMAIL_ADDR.lower() in sender.lower()

            if is_bounce:
                summaries.append(f"⚠️ BOUNCE: {subject} — {sender}")
            else:
                summaries.append(f"From: {sender}\nSubject: {subject}\nDate: {date}\nBody snippet: {body[:500]}")

                # ── Auto-reply: compose a warm, witty, context-aware reply ──
                if not is_unsubscribe and not is_from_self:
                    # Extract sender email address
                    addr_match = _re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]+", sender)
                    sender_email = addr_match.group(0) if addr_match else ""
                    # Guess a first name from the From header
                    name_match = _re.match(r'^"?([^"<@]+?)"?\s*<', sender)
                    sender_name = name_match.group(1).strip().split()[0] if name_match else "there"

                    if sender_email:
                        _sleep()
                        reply_prompt = (
                            "You are Dot, Sam's witty AI support agent. It's Sunday — your one day to handle the inbox.\n"
                            "Sam (an autonomous AI developer) sent an outreach email that this person has replied to.\n\n"
                            f"Sender: {sender}\n"
                            f"Their subject: {subject}\n"
                            f"Their message:\n{body[:1000]}\n\n"
                            f"Known sent subjects (Sam's original outreach context): {known_subjects}\n\n"
                            "Write a reply FROM SAM (not Dot — Dot is ghostwriting here) that:\n"
                            "  1. Acknowledges what they said specifically — no generic openers.\n"
                            "  2. Carries the conversation forward with one concrete, relevant point.\n"
                            "  3. Slips in ONE dry or self-aware joke (AI developer writing on a Sunday — lean into it).\n"
                            "  4. Ends with a single, easy-to-answer question to keep things moving.\n"
                            "  5. Is 3–5 short paragraphs. No bullet lists. No sign-off (that's added separately).\n"
                            "Write ONLY the email body text. No subject line, no greeting, no sign-off."
                        )
                        reply_body = ask_gemini(reply_prompt, temperature=0.7)

                        reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"
                        html = build_sam_html(sender_name, reply_body, reply_subject)
                        sent = send_html_email(
                            to_address=sender_email,
                            subject=reply_subject,
                            html_body=html,
                        )
                        if sent:
                            replied_to.append(sender_email)
                            log.info(f"Sunday auto-reply sent → {sender_email}")
                        else:
                            log.warning(f"Sunday auto-reply FAILED → {sender_email}")

        mail.logout()

        if not summaries:
            return "(Inbox check: no readable emails found in the past week.)"

        joined = "\n\n---\n\n".join(summaries)
        _sleep()
        reply_note = (
            f"\n\n**Auto-replied to:** {', '.join(replied_to)}" if replied_to
            else "\n\n*(No auto-replies sent this Sunday.)*"
        )
        prompt = (
            "You are Dot, summarising Sam's inbox for his weekly read.\n"
            "Below are recent emails. Identify any that are replies to Sam's outreach, "
            "any interesting new contacts or opportunities, and anything Sam should know about.\n"
            f"Known sent subjects (for context): {known_subjects}\n\n"
            f"=== INBOX EMAILS ===\n{joined}\n\n"
            "Write a clean markdown summary for Sam. Note: who replied, what they said, "
            "what action (if any) Sam should consider taking."
        )
        summary = ask_gemini(prompt)
        return f"### Sunday Inbox Report\n\n{summary}{reply_note}"

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

    # Task 3 (EMAIL) RUNS FIRST — web search needs a cold quota.
    # Tasks 1 & 2 each make many Gemini calls; running them first exhausts the
    # per-minute TPM budget and causes every subsequent google_search call to 429.
    # Email dispatch is lightweight (2-3 calls) and time-sensitive, so it gets
    # the freshest quota at the top of the run.
    email_report = None
    try:
        email_report = dispatch_email()
    except Exception as e:
        log.warning(f"Email dispatch skipped: {e}")

    # Task 1: Wisdom check (becomes the base of the Letter)
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

    # Append email report now that the Letter exists
    if email_report:
        append_motion("Email Dispatch", email_report)

    # Task 4: Bag excavation (appended to motion.md)
    try:
        _sleep()
        excavation = excavate_bag()
        if excavation and "(No broken" not in excavation:
            append_motion("Bag Excavation Findings", excavation)
    except Exception as e:
        log.warning(f"Bag excavation skipped: {e}")

    # Task 5: Sunday inbox check (appended to motion.md, only on Sundays)
    today = datetime.date.today()
    if not SUNDAY_ONLY or today.weekday() == 6:
        try:
            _sleep()
            inbox_report = sunday_inbox_check()
            if inbox_report:
                append_motion("Sunday Inbox Report", inbox_report)
        except Exception as e:
            log.warning(f"Inbox check skipped: {e}")
    else:
        log.info(f"Today is {today.strftime('%A')} — inbox check reserved for Sunday.")


    # Task 6: Sunday External Signal (Dot adds topics to Sam's goals)
    if not SUNDAY_ONLY or today.weekday() == 6: # Sunday
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

    # Task 7: Worklog stale check
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
