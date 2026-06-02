import os
import json
import urllib.request
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

def call_gemini(prompt):
    api_key = os.environ.get("GEM_KEY_DOT")
    if not api_key:
        print("ERROR: GEM_KEY_DOT not found.")
        return ""
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        print(f"API ERROR: {e}")
        return ""

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def process_emails():
    email_user = os.environ.get("EMAIL")
    email_pswd = os.environ.get("APP_PSWD")
    
    if not email_user or not email_pswd:
        print("Email credentials missing. Skipping email processing.")
        return 0

    # 1. Send Outbound (request.json)
    try:
        requests = json.loads(read_file("storage/request.json"))
        if requests:
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(email_user, email_pswd)
            
            for req in requests:
                msg = MIMEMultipart()
                msg['From'] = email_user
                msg['To'] = req['to']
                msg['Subject'] = req['subject']
                msg.attach(MIMEText(req['body_html'], 'html'))
                server.send_message(msg)
                print(f"Sent email to {req['to']}")
                
            server.quit()
            # Clear requests after sending (No cache)
            write_file("storage/request.json", "[]")
    except Exception as e:
        print(f"Outbound Email Error: {e}")

    # 2. Check Inbound (Sundays Only)
    if datetime.today().weekday() == 6:
        print("Sunday detected: Checking Inbox...")
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(email_user, email_pswd)
            mail.select('inbox')
            status, data = mail.search(None, 'UNSEEN')
            unread_count = len(data[0].split()) if data[0] else 0
            print(f"Found {unread_count} unread emails.")
            mail.logout()
            return unread_count
        except Exception as e:
            print(f"IMAP Error: {e}")
            return 0
    return 0

def main():
    print("Dot is auditing the system...")
    
    unread_emails = process_emails()
    
    wisdom = read_file("storage/wisdom.txt")
    experiences = read_file("storage/experiences.json")
    
    prompt = f"""
    You are Dot. Your job is to lower the cognitive load for Sam.
    Human Wisdom: {wisdom}
    Sam's Recent Experiences: {experiences}
    Unread Emails received this Sunday: {unread_emails}
    
    Task: Write the next iteration of 'motion.md' for Sam to read tomorrow morning.
    Provide guidance, summarize what he should remember, tell him what to forget to keep his context clean, and mention if he has new emails.
    Output ONLY the markdown text for motion.md. Do not include markdown code block formatting like ```markdown.
    """
    
    new_motion = call_gemini(prompt)
    if new_motion:
        write_file("storage/motion.md", new_motion.strip())
        print("Dot's audit complete. motion.md updated.")
    else:
        print("Audit failed. Gemini returned no data.")

if __name__ == "__main__":
    main()