"""
dot.py
Dot — the communication agent.
Pure orchestration. All logic lives in _starter_pack.py.
Workflow: fetch inbox → load memory → per email: extract idea, context-aware reply → save memory → summarise → email owner
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from modules._starter_pack import (
    _fetch_inbox,
    _extract_idea_via_gemini,
    _should_reply_via_gemini,
    _generate_reply_via_gemini,
    _summarise_body_via_gemini,
    _reply_to_sender,
    _summarise_run_via_gemini,
    _send_email,
    _update_idea,
    _load_memory,
    _save_memory,
    _get_contact,
    _update_contact,
)

GEM_KEY     = os.environ["GEM_KEY_DOT"]
OWNER_EMAIL = os.environ["OWNER_EMAIL"]
DOT_EMAIL   = os.environ["EMAIL"]
APP_PSWD    = os.environ["APP_PSWD"]
IDEA_QUEUE  = "idea_queue.json"
MEMORY_PATH = "dot_memory.json"


def main():
    print("[Dot] Online.")

    emails = _fetch_inbox(DOT_EMAIL, APP_PSWD)

    if not emails:
        print("[Dot] Inbox empty.")
        _send_email(OWNER_EMAIL, "[Dot] Quiet inbox", "Nothing new. Sam is still cooking.", DOT_EMAIL, APP_PSWD)
        return

    print(f"[Dot] {len(emails)} email(s) to process.")
    memory = _load_memory(MEMORY_PATH)
    processed = []

    for mail in emails:
        sender  = mail.get("sender", "")
        subject = mail.get("subject", "")
        body    = mail.get("body", "")

        contact = _get_contact(memory, sender)

        # extract idea → queue
        idea = _extract_idea_via_gemini(sender, subject, body, GEM_KEY)
        _update_idea(idea, IDEA_QUEUE)
        print(f"[Dot] Idea queued from {sender}: {idea}")

        # context-aware reply decision
        replied = False
        if _should_reply_via_gemini(sender, subject, body, contact, GEM_KEY):
            reply = _generate_reply_via_gemini(sender, subject, body, contact, GEM_KEY)
            replied = _reply_to_sender(sender, subject, reply, DOT_EMAIL, APP_PSWD)
            print(f"[Dot] Replied to {sender}: {replied}")
        else:
            print(f"[Dot] Skipping reply to {sender} (Gemini said no).")

        # summarise body for memory (short, for storage)
        body_summary = _summarise_body_via_gemini(body, GEM_KEY)
        memory = _update_contact(memory, sender, subject, body_summary, idea, replied)
        processed.append((sender, idea, replied))

    _save_memory(memory, MEMORY_PATH)
    print("[Dot] Memory updated.")

    summary = _summarise_run_via_gemini(processed, GEM_KEY)
    _send_email(OWNER_EMAIL, "[Dot] Daily Summary", summary, DOT_EMAIL, APP_PSWD)
    print("[Dot] Summary sent. Done.")


if __name__ == "__main__":
    main()
