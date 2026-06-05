"""
_starter_pack.py
Core utility functions for Sam and Dot agents.
Convention: function names start with '_', all lowercase, underscores for spaces.
"""

import os
import json
import time
import random
import subprocess
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

GEMINI_MODEL = "gemini-2.0-flash-lite"


# ── core gemini ──────────────────────────────────────────────

def _ask_gemini(prompt: str, api_key: str) -> str:
    """Ask Gemini a question and return the text response."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()


def _ask_gemini_json(prompt: str, api_key: str) -> dict | list:
    """Ask Gemini a question, expect JSON back. Strips markdown fences."""
    raw = _ask_gemini(prompt, api_key)
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(clean)


# ── file system ──────────────────────────────────────────────

def _create_file(path: str, content: str) -> bool:
    """Write content to a file at path. Returns True on success."""
    try:
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(path, "w") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"[_create_file] Error: {e}")
        return False


def _call_delay(seconds: int) -> None:
    """Sleep for given seconds. Useful between API calls."""
    time.sleep(seconds)


def _run_script(script_path: str) -> tuple:
    """Run a Python script. Returns (stdout, stderr, returncode)."""
    result = subprocess.run(["python", script_path], capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode


# ── idea queue ───────────────────────────────────────────────

def _update_idea(idea: str, queue_path: str = "idea_queue.json") -> bool:
    """Append a new idea to the idea queue JSON file."""
    try:
        with open(queue_path, "r") as f:
            data = json.load(f)
        data["ideas"].append({"idea": idea, "timestamp": time.time()})
        with open(queue_path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"[_update_idea] Error: {e}")
        return False


def _pop_idea(queue_path: str = "idea_queue.json") -> str | None:
    """Remove and return the oldest idea from the queue. None if empty."""
    try:
        with open(queue_path, "r") as f:
            data = json.load(f)
        if not data["ideas"]:
            return None
        idea = data["ideas"].pop(0)["idea"]
        with open(queue_path, "w") as f:
            json.dump(data, f, indent=2)
        return idea
    except Exception as e:
        print(f"[_pop_idea] Error: {e}")
        return None


def _generate_idea(api_key: str) -> str:
    """Ask Gemini to generate a fresh creative Python script idea."""
    prompt = (
        "Give me one short, creative, weird Python script idea in one sentence. "
        "Think outside the box. No explanations, just the idea."
    )
    return _ask_gemini(prompt, api_key)


def _get_or_generate_idea(queue_path: str, api_key: str) -> str:
    """Pop an idea from the queue, or ask Gemini to generate one if empty."""
    idea = _pop_idea(queue_path)
    if idea:
        print(f"[Sam] Idea from queue: {idea}")
        return idea
    idea = _generate_idea(api_key)
    print(f"[Sam] Gemini generated idea: {idea}")
    _update_idea(idea, queue_path)
    return idea


# ── planning & building ──────────────────────────────────────

def _make_plan(idea: str, module_taglines: list, api_key: str) -> dict:
    """
    Takes idea + up to 7 random module taglines, asks Gemini to plan a script
    using up to 4 suitable modules. Returns structured plan dict.
    """
    sample = random.sample(module_taglines, min(7, len(module_taglines)))
    taglines_str = "\n".join(f"- {t}" for t in sample)
    prompt = (
        f"You are a Python script planner. Given this idea:\n'{idea}'\n\n"
        f"And these available modules (taglines):\n{taglines_str}\n\n"
        f"Choose up to 4 suitable modules and create a structured plan. "
        f"Respond ONLY as JSON with keys: 'script_name' (s_*_script), "
        f"'tagline' (one line), 'modules_used' (list), 'steps' (list of step strings)."
    )
    return _ask_gemini_json(prompt, api_key)


def _execute_plan(plan: dict, api_key: str) -> str:
    """Takes a plan dict and generates Python script content via Gemini."""
    prompt = (
        f"Write a Python script named '{plan['script_name']}' that implements this plan:\n"
        f"Tagline: {plan['tagline']}\n"
        f"Steps: {json.dumps(plan['steps'])}\n"
        f"Modules used: {plan['modules_used']}\n\n"
        f"Rules: each function under 30 lines, use S_ prefix and CAPS for Sam functions. "
        f"Return ONLY valid Python code, no markdown fences."
    )
    return _ask_gemini(prompt, api_key)


def _make_new_module_with_tag(module_name: str, tagline: str, modules_dir: str = "modules") -> bool:
    """Create an empty module file with a tagline comment."""
    content = f'"""\n{module_name}.py\nTagline: {tagline}\n"""\n\n# Functions go here\n'
    path = os.path.join(modules_dir, f"{module_name}.py")
    return _create_file(path, content)


def _make_module_tagline(module_name: str, context: str, api_key: str) -> str:
    """Ask Gemini to write a one-line tagline for a new module."""
    prompt = (
        f"Write a one-line tagline for a Python module named '{module_name}' "
        f"used in: {context}. Be concise."
    )
    return _ask_gemini(prompt, api_key)


def _decide_script(idea: str, script_taglines: list, api_key: str) -> str:
    """
    Takes idea + up to 4 random script taglines.
    Returns the best matching script filename, or 'none' if nothing fits.
    """
    sample = random.sample(script_taglines, min(4, len(script_taglines)))
    taglines_str = "\n".join(f"- {t}" for t in sample)
    prompt = (
        f"Given this idea: '{idea}'\n"
        f"And these scripts:\n{taglines_str}\n\n"
        f"Return ONLY the script filename (e.g. s_example_script.py) that best matches. "
        f"If nothing fits well, return exactly: none"
    )
    return _ask_gemini(prompt, api_key).strip()


def _save_script(plan: dict, code: str, scripts_dir: str, api_key: str) -> str:
    """Write generated script to disk and register it in tag registry."""
    from modules import register_entry
    name = plan["script_name"]
    if not name.endswith(".py"):
        name += ".py"
    path = os.path.join(scripts_dir, name)
    _create_file(path, code)
    register_entry(name, plan["tagline"], "script")
    print(f"[Sam] Script saved: {path}")
    return path


def _ensure_modules_exist(plan: dict, modules_dir: str, api_key: str) -> None:
    """Create stub modules from the plan if they don't already exist."""
    from modules import register_entry
    for mod_name in plan.get("modules_used", []):
        mod_path = os.path.join(modules_dir, f"{mod_name}.py")
        if not os.path.exists(mod_path):
            tagline = _make_module_tagline(mod_name, plan["tagline"], api_key)
            _make_new_module_with_tag(mod_name, tagline, modules_dir)
            register_entry(mod_name, tagline, "module")
            print(f"[Sam] Created module stub: {mod_name}")


# ── dot: gmail (gemini web search) ───────────────────────────

def _fetch_inbox_via_gemini(api_key: str) -> list:
    """
    Ask Gemini (with web/gmail tool) to summarise unread emails.
    Returns list of dicts: {sender, subject, body}.
    """
    prompt = (
        "Check the Gmail inbox and return up to 5 unread emails. "
        "For each email return a JSON array where every item has keys: "
        "'sender', 'subject', 'body' (first 300 chars of body). "
        "Return ONLY the JSON array, no markdown."
    )
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        GEMINI_MODEL,
        tools="gmail_read_message",   # Gemini native Gmail tool
    )
    response = model.generate_content(prompt)
    raw = response.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except Exception:
        return []


def _extract_idea_via_gemini(sender: str, subject: str, body: str, api_key: str) -> str:
    """Ask Gemini to extract one Python script idea from an email."""
    prompt = (
        f"Email from: {sender}\nSubject: {subject}\nBody: {body}\n\n"
        f"Extract ONE actionable Python script idea in one sentence. "
        f"If nothing obvious, invent one inspired by the topic. "
        f"Return ONLY the idea sentence."
    )
    return _ask_gemini(prompt, api_key)





def _summarise_run_via_gemini(processed: list, api_key: str) -> str:
    """Ask Gemini to write a friendly daily summary from processed email data."""
    items = "\n".join(
        f"- From: {s} | Idea: {i} | Replied: {r}"
        for s, i, r in processed
    )
    prompt = (
        f"Write a short daily summary for the owner about these email interactions:\n"
        f"{items}\n\n"
        f"Keep it friendly, under 10 lines. Sign off as Dot."
    )
    return _ask_gemini(prompt, api_key)


# ── dot: send email ──────────────────────────────────────────

def _send_email(to: str, subject: str, body: str, dot_email: str, app_pswd: str) -> bool:
    """Send an email via Gmail SMTP using app password."""
    try:
        msg = MIMEMultipart()
        msg["From"] = dot_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(dot_email, app_pswd)
            server.sendmail(dot_email, to, msg.as_string())
        return True
    except Exception as e:
        print(f"[_send_email] Error: {e}")
        return False


def _reply_to_sender(sender: str, subject: str, reply_body: str, dot_email: str, app_pswd: str) -> bool:
    """Send a reply to the original sender."""
    reply_subject = subject if subject.startswith("Re:") else f"Re: {subject}"
    return _send_email(sender, reply_subject, reply_body, dot_email, app_pswd)


# ── dot: memory ──────────────────────────────────────────────

def _load_memory(memory_path: str = "dot_memory.json") -> dict:
    """Load Dot's contact memory from disk."""
    with open(memory_path, "r") as f:
        return json.load(f)


def _save_memory(memory: dict, memory_path: str = "dot_memory.json") -> None:
    """Save Dot's contact memory to disk."""
    with open(memory_path, "w") as f:
        json.dump(memory, f, indent=2)


def _get_contact(memory: dict, sender: str) -> dict:
    """Return contact record for sender, or empty record if new."""
    return memory["contacts"].get(sender, {
        "sender": sender,
        "thread": [],
        "ideas_extracted": [],
        "replied_count": 0,
        "last_replied": None,
    })


def _update_contact(memory: dict, sender: str, subject: str,
                    body_summary: str, idea: str, replied: bool) -> dict:
    """Update contact record after processing an email. Returns updated memory."""
    contact = _get_contact(memory, sender)
    contact["thread"].append({
        "subject": subject,
        "summary": body_summary[:200],
        "timestamp": time.time(),
        "replied": replied,
    })
    contact["ideas_extracted"].append(idea)
    if replied:
        contact["replied_count"] += 1
        contact["last_replied"] = time.time()
    memory["contacts"][sender] = contact
    return memory


def _format_thread_for_gemini(contact: dict) -> str:
    """Format a contact's conversation history as text for Gemini context."""
    if not contact["thread"]:
        return "No previous conversation."
    lines = []
    for t in contact["thread"][-5:]:
        ts = time.strftime("%Y-%m-%d", time.localtime(t["timestamp"]))
        lines.append(f"[{ts}] Subject: {t['subject']} | Summary: {t['summary']} | Replied: {t['replied']}")
    return "\n".join(lines)


def _should_reply_via_gemini(sender: str, subject: str, body: str,
                              contact: dict, api_key: str) -> bool:
    """Ask Gemini if Dot should reply, given full conversation history."""
    thread = _format_thread_for_gemini(contact)
    prompt = (
        f"You are Dot, a smart AI assistant. Decide if you should reply to this email.\n\n"
        f"Sender: {sender}\nSubject: {subject}\nBody: {body[:400]}\n\n"
        f"Previous conversation with this person:\n{thread}\n\n"
        f"Rules:\n"
        f"- Do NOT reply if you already replied to the same subject recently.\n"
        f"- Do NOT reply to automated/spam/newsletter emails.\n"
        f"- Do NOT reply if the email is just a notification with no question.\n"
        f"- DO reply if they asked something or seem to expect a response.\n\n"
        f"Answer only YES or NO."
    )
    return _ask_gemini(prompt, api_key).strip().upper().startswith("YES")


def _generate_reply_via_gemini(sender: str, subject: str, body: str,
                                contact: dict, api_key: str) -> str:
    """Ask Gemini to write a context-aware reply as Dot."""
    thread = _format_thread_for_gemini(contact)
    ideas = ", ".join(contact["ideas_extracted"][-3:]) if contact["ideas_extracted"] else "none yet"
    prompt = (
        f"You are Dot, an AI assistant to a developer named Sam.\n\n"
        f"Replying to {sender}.\nSubject: {subject}\nTheir message: {body[:600]}\n\n"
        f"Conversation history:\n{thread}\n\n"
        f"Ideas previously extracted from them: {ideas}\n\n"
        f"Write a short (3-5 sentence), helpful, context-aware, slightly witty reply. "
        f"Do NOT repeat things you've already said. Sign off as 'Dot'."
    )
    return _ask_gemini(prompt, api_key)


def _summarise_body_via_gemini(body: str, api_key: str) -> str:
    """Ask Gemini for a one-line summary of an email body for memory storage."""
    prompt = f"Summarise this email body in one sentence (max 20 words):\n{body[:600]}"
    return _ask_gemini(prompt, api_key)
