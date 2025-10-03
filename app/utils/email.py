import os
import ssl
from email.message import EmailMessage
import aiosmtplib

MAIL_BACKEND = os.getenv("MAIL_BACKEND", "smtp").lower()
MAIL_SERVER = os.getenv("MAIL_SERVER", "127.0.0.1")
MAIL_PORT = int(os.getenv("MAIL_PORT", "1025"))
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_FROM = os.getenv("MAIL_FROM", "dev@local.test")
MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "false").lower() == "true"
MAIL_SSL = os.getenv("MAIL_SSL", "false").lower() == "true"

class EmailSender:
    async def send_email(self, to: str, subject: str, html_body: str, text_body: str | None = None):
        if MAIL_BACKEND == "console":
            print("=== EMAIL OUT ===")
            print(f"From: {MAIL_FROM}")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            if text_body:
                print(f"Text: {text_body}")
            print(f"HTML: {html_body}")
            print("=== END EMAIL ===")
            return
        msg = EmailMessage()
        msg["From"] = MAIL_FROM
        msg["To"] = to
        msg["Subject"] = subject
        if text_body:
            msg.set_content(text_body)
        msg.add_alternative(html_body, subtype="html")
        context = ssl.create_default_context()
        kwargs = {
            "hostname": MAIL_SERVER,
            "port": MAIL_PORT,
            "timeout": 30,
            "tls_context": context,
        }
        if MAIL_SSL:
            kwargs["use_tls"] = True
        else:
            kwargs["start_tls"] = MAIL_STARTTLS
        if MAIL_USERNAME and MAIL_PASSWORD:
            kwargs["username"] = MAIL_USERNAME
            kwargs["password"] = MAIL_PASSWORD
        await aiosmtplib.send(msg, **kwargs)

email_sender = EmailSender()
