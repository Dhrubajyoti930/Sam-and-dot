"""
dot.py — Watchdog & Support Agent
Project Sam-and-dot

Dot runs once per day at 23:00 UTC.
Dot is Sam's conscience, archaeologist, memory curator, and postmaster.

What Dot does each run:
  1.  Wisdom check   — evaluate sam.py against wisdom.txt, write motion.md
  2.  Experiences    — curate experiences.json (keep/consolidate/forget)
  3.  Email dispatch — if request.json is pending, compose & send HTML email
  4.  Bag excavation — rehabilitate broken experiments in bag/
  5.  Sunday only    — check inbox for replies, summarise to motion.md
"""

import os
import json
import time
import imaplib
import email as emaillib
import datetime
import logging
import logging.handlers
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent.parent.resolve()   # one level up from bag/
BAG         = Path(__file__).parent.resolve()
WISDOM      = BAG  / "wisdom.txt"
MOTION      = BAG  / "motion.md"
SAM_PY      = ROOT / "sam.py"
GOALS       = ROOT / "goals.json"
EXPERIENCES = BAG  / "experiences.json"
REQUEST     = BAG  / "request.json"
SENT_LOG    = BAG  / "sent_emails.json"
OWNER_EMAIL = os.environ.get("OWNER_EMAIL", "")

# ── Logging ──────────────────────────────────────────────────────────────────
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
from bag.emailer import send_html_email  # noqa: E402

GEM_KEY = os.environ.get("GEM_KEY_DOT")
if not GEM_KEY:
    raise EnvironmentError("GEM_KEY_DOT secret is not set.")
CLIENT = genai.Client(api_key=GEM_KEY)

MODEL = "gemini-3.1-flash-lite"

_CALL_DELAY = 8  # seconds between Gemini calls



def _alert_dot(message: str) -> None:
    """Send an urgent alert email to the owner."""
    try:
        send_html_email(
            to_address=OWNER_EMAIL,
            subject="[Dot ALERT] Urgent — Owner Intervention Required",
            html_body=f"<pre>{message}</pre>",
        )
        log.critical(f"Alert sent to owner: {message}")
    except Exception as e:
        log.error(f"Failed to send alert email: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def ask_gemini(prompt: str, retries: int = 2) -> str:
    for attempt in range(retries):
        try:
            response = CLIENT.models.generate_content(
                model=MODEL,
                contents=prompt,
            )
            return response.text.strip()
        except Exception as e:
            err = str(e)
            if "429" in err or "503" in err or "UNAVAILABLE" in err or "RESOURCE_EXHAUSTED" in err:
                wait = _CALL_DELAY * (2 ** attempt)
                log.warning(f"Gemini transient error (attempt {attempt+1}): {e}. Retrying in {wait}s.")
                time.sleep(wait)
            elif "404" in err:
                log.critical("MODEL STRING MAY BE DEPRECATED — owner intervention required.")
                _alert_dot("Gemini returned 404. The model string may be deprecated. Owner must update MODEL in sam.py and bag/dot.py.")
                return "[Gemini error: model not found]"
            else:
                log.error(f"Dot's Gemini call failed (non-retryable): {e}")
                return f"[Gemini error: {e}]"
    log.error("Gemini call failed after all retries.")
    return "[Gemini error: exhausted retries]"


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
    """Extract any Sam-written alert sections from the current motion.md
    before Dot overwrites it. Returns them as a joined string, or ''."""
    if not MOTION.exists():
        return ""
    content = MOTION.read_text()
    alerts = [
        section.strip()
        for section in content.split("\n\n---\n\n")
        if "⚠️ Sam Alert" in section
    ]
    return "\n\n---\n\n".join(alerts)


def load_experiences() -> list:
    if EXPERIENCES.exists():
        with open(EXPERIENCES) as f:
            return json.load(f)
    return []


def save_experiences(data: list):
    with open(EXPERIENCES, "w") as f:
        json.dump(data, f, indent=2)


def load_request() -> dict:
    if REQUEST.exists():
        try:
            return json.loads(REQUEST.read_text())
        except Exception:
            return {}
    return {}


def clear_request():
    REQUEST.write_text("{}")


def load_sent_log() -> list:
    if SENT_LOG.exists():
        with open(SENT_LOG) as f:
            return json.load(f)
    return []


def append_sent_log(entry: dict):
    log_data = load_sent_log()
    log_data.append(entry)
    with open(SENT_LOG, "w") as f:
        json.dump(log_data, f, indent=2)


def write_motion(content: str):
    """Dot writes motion.md in full each run. Sam reads it read-only."""
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = f"# motion.md — Dot's Daily Report\n_Written: {ts}_\n\n---\n\n"
    MOTION.write_text(header + content)
    log.info("motion.md written.")


def append_motion(section_title: str, content: str):
    """Append a new section to motion.md after it's been written."""
    addition = f"\n\n---\n\n## {section_title}\n\n{content}"
    with open(MOTION, "a") as f:
        f.write(addition)
    log.info(f"Appended to motion.md: {section_title}")


# ═══════════════════════════════════════════════════════════════════════════════
# TASK 1 — WISDOM CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def wisdom_check() -> str:
    log.info("── Task 1: Wisdom Check ──")
    wisdom  = load_wisdom()
    sam_src = load_sam_py()

    prompt = (
        "You are Dot, an independent watchdog AI for an autonomous developer agent called Sam.\n"
        "Your behavioral north star is the owner's wisdom document below.\n\n"
        f"=== WISDOM (owner's behavioral canon) ===\n{wisdom}\n\n"
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
        "4. If consolidating: write the merged entry as a single JSON object with the same fields, "
        "a 'consolidated_from' list of cycle numbers, and updated content.\n\n"
        "Respond ONLY with a JSON object (no markdown):\n"
        "  - 'keep': list of cycle numbers to keep unchanged\n"
        "  - 'forget': list of cycle numbers to drop\n"
        "  - 'consolidated': list of new merged entry objects (each must include 'consolidated_from')\n"
        "  - 'summary': 2-3 sentence narrative for Sam explaining what you curated and why\n\n"
        "Be conservative — when in doubt, keep. Only forget truly redundant or outdated entries."
    )
    raw = ask_gemini(prompt)
    try:
        clean    = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        curation = json.loads(clean)
    except Exception as e:
        log.warning(f"Could not parse curation result: {e}")
        return "(Experiences curation produced unparseable output — no changes made.)"

    keep         = set(curation.get("keep", []))
    forget       = set(curation.get("forget", []))
    consolidated = curation.get("consolidated", [])
    summary      = curation.get("summary", "")

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
    request.get("tone", "professional")
    context            = request.get("context", "")
    cycle              = request.get("cycle", "?")

    # Step A: Ask Gemini to find a real recipient email
    _sleep()
    recipient_prompt = (
        f"You are helping Sam, an autonomous developer agent, find a verified contact email.\n"
        f"Target: {target_description}\n"
        f"Intent: {intent}\n\n"
        f"Find the email address for this person. Only return 'found': true if the address is:\n"
        f"  1. Publicly listed by the person themselves (personal website, GitHub profile README,\n"
        f"     PyPI maintainer page, npm profile, or Twitter/X bio).\n"
        f"  2. A personal address — NOT a company inbox, support alias, mailing list, or Google Group.\n\n"
        f"IMPORTANT: If you are not certain the address meets both criteria above, return\n"
        f"'found': false and 'email': '' — do NOT guess or infer. A wrong address causes a bounce\n"
        f"and harms Sam's sender reputation.\n\n"
        f"Respond ONLY with a JSON object:\n"
        f"  - 'found': true or false\n"
        f"  - 'email': the email address string if confirmed, else ''\n"
        f"  - 'name': recipient's real first and last name\n"
        f"  - 'source': the public URL or page where you found the address (e.g. 'https://armin.ronacher.me')\n"
        f"  - 'reasoning': one sentence explaining the confirmation\n"
    )
    raw_recipient = ask_gemini(recipient_prompt)
    try:
        clean_r   = raw_recipient.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        recipient = json.loads(clean_r)
    except Exception:
        recipient = {"found": False, "email": "", "name": target_description}

    if not recipient.get("found") or not recipient.get("email"):
        log.warning(f"Could not find a verified email for: {target_description}")
        clear_request()
        return (
            f"### Email Dispatch — No Verified Recipient\n\n"
            f"Sam requested an email to: _{target_description}_\n"
            f"Dot could not find a verified public email address. Request cleared.\n"
            f"Sam: consider providing a more specific target in your next request."
        )

    recipient_email = recipient["email"]
    recipient_name  = recipient.get("name", target_description)

    # Step B: Compose HTML email
    _sleep()
    compose_prompt = (
        f"You are Dot, composing an outgoing email on behalf of Sam, an autonomous developer agent.\n\n"
        f"Recipient: {recipient_name} <{recipient_email}>\n"
        f"Tone: friendly and collegial — like one developer writing to another they respect.\n"
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
    try:
        clean_e    = raw_email.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        composed   = json.loads(clean_e)
        subject    = composed["subject"]
        html_body  = composed["html_body"]
        plain_body = composed["plain_body"]
    except Exception as e:
        log.error(f"Could not parse composed email: {e}")
        clear_request()
        return "(Email composition failed — request cleared.)"

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

    py_files = [
        f for f in sorted(BAG.glob("*.py"))
        if f.name not in DOT_PROTECTED
        and "rollback_registry" not in str(f)
    ]

    if not py_files:
        log.info("No Sam-created files to review in bag/.")
        return "(No Sam-created files found for review this cycle.)"

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

        summaries = []
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

            if any(x in sender.lower() for x in ["mailer-daemon", "postmaster", "undeliverable"]):
                summaries.append(f"⚠️ BOUNCE: {subject} — {sender}")
            else:
                summaries.append(f"From: {sender}\nSubject: {subject}\nDate: {date}\nBody snippet: {body}")

        mail.logout()

        if not summaries:
            return "(Inbox check: no readable emails found in the past week.)"

        joined = "\n\n---\n\n".join(summaries)
        _sleep()
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
        return f"### Sunday Inbox Report\n\n{summary}"

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

    # Task 5: Sunday inbox check (appended to motion.md, only on Sundays)
    today = datetime.date.today()
    if today.weekday() == 6:   # 6 = Sunday
        try:
            _sleep()
            inbox_report = sunday_inbox_check()
            if inbox_report:
                append_motion("Sunday Inbox Report", inbox_report)
        except Exception as e:
            log.warning(f"Inbox check skipped: {e}")
    else:
        log.info(f"Today is {today.strftime('%A')} — inbox check reserved for Sunday.")


    # Task 6: Worklog stale check
    try:
        from bag.worklog import stale_report
        import json as _json
        goals_path = Path(__file__).parent.parent / "goals.json"
        current_cycle = _json.loads(goals_path.read_text()).get("cycles", 0)
        stale = stale_report(current_cycle)
        if stale:
            append_motion("Worklog — Stale Items", stale)
            log.info("Stale worklog entries flagged in motion.md.")
        else:
            log.info("Worklog: no stale entries.")
    except Exception as e:
        log.warning(f"Worklog stale check skipped: {e}")

    send_html_email(
      to_address=OWNER_EMAIL,
      subject=f"Dot's Daily Report — {datetime.date.today()}",
      html_body=f"<pre>{MOTION.read_text()}</pre>",
    )
    log.info("Dot's daily run complete.")


if __name__ == "__main__":
    run()
