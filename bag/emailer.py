"""
emailer.py — Standalone Email Utility
Project Sam-and-dot

This module is called by dot.py for email dispatch.
It can also be run standalone for testing:
  python bag/emailer.py --to test@example.com --subject "Hello" --body "Test"

Credentials are read from environment: EMAIL, APP_PSWD
"""

import os
import sys
import json
import argparse
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from pathlib              import Path


def send_html_email(
    to_address: str,
    subject:    str,
    html_body:  str,
    plain_body: str = "",
    from_address: str = "",
    app_password: str = "",
) -> bool:
    """
    Send an HTML email via Gmail SMTP SSL.

    Args:
        to_address:   Recipient email.
        subject:      Subject line.
        html_body:    HTML-formatted body.
        plain_body:   Plain-text fallback (auto-stripped from HTML if empty).
        from_address: Sender Gmail address (defaults to EMAIL env var).
        app_password: Gmail App Password (defaults to APP_PSWD env var).

    Returns:
        True on success, False on failure.
    """
    from_address = from_address or os.environ.get("EMAIL", "")
    app_password = app_password or os.environ.get("APP_PSWD", "")

    if not from_address or not app_password:
        print("[emailer] ERROR: EMAIL and APP_PSWD must be set.")
        return False

    if not plain_body:
        import re
        plain_body = re.sub(r"<[^>]+>", "", html_body).strip()

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = from_address
    msg["To"]      = to_address

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body,  "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(from_address, app_password)
            server.sendmail(from_address, to_address, msg.as_string())
        print(f"[emailer] Sent → {to_address}: '{subject}'")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[emailer] AUTH FAILED — check EMAIL and APP_PSWD.")
        return False
    except Exception as e:
        print(f"[emailer] SMTP error: {e}")
        return False


def build_sam_html(
    recipient_name: str,
    body_content:   str,
    subject:        str,
) -> str:
    """
    Build a clean, inline-CSS HTML email in Sam's voice.
    body_content should be the main message paragraphs as plain text.
    """
    paragraphs = "".join(
        f"<p style='margin:0 0 12px 0;'>{p.strip()}</p>"
        for p in body_content.strip().split("\n\n")
        if p.strip()
    )
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{subject}</title></head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:32px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0"
               style="background:#ffffff;border-radius:8px;overflow:hidden;
                      box-shadow:0 2px 8px rgba(0,0,0,0.08);">

          <!-- Header -->
          <tr>
            <td style="background:#1a1a2e;padding:28px 36px;">
              <span style="color:#e0e0ff;font-size:18px;font-weight:600;letter-spacing:0.5px;">
                Sam · Autonomous Developer
              </span>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:36px 36px 24px 36px;color:#2c2c2c;font-size:15px;line-height:1.7;">
              <p style="margin:0 0 12px 0;">Hi {recipient_name},</p>
              {paragraphs}
              <p style="margin:24px 0 0 0;">
                Best,<br/>
                <strong>Sam</strong><br/>
                <span style="color:#888;font-size:13px;">Sam-and-dot · Autonomous Developer Agent</span>
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#f9f9f9;padding:16px 36px;border-top:1px solid #ececec;">
              <span style="color:#aaa;font-size:12px;">
                This message was composed and sent by Sam, an autonomous AI developer agent,
                on {ts}. To unsubscribe from future messages, simply reply "unsubscribe".
              </span>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


# ── CLI interface ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sam-and-dot standalone emailer")
    parser.add_argument("--to",      required=True,  help="Recipient email address")
    parser.add_argument("--name",    default="there", help="Recipient name for greeting")
    parser.add_argument("--subject", required=True,  help="Email subject line")
    parser.add_argument("--body",    required=True,  help="Plain-text body (paragraphs separated by \\n\\n)")
    args = parser.parse_args()

    html = build_sam_html(args.name, args.body, args.subject)
    success = send_html_email(
        to_address=args.to,
        subject=args.subject,
        html_body=html,
    )
    sys.exit(0 if success else 1)
