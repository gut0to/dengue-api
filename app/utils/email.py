import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailSender:
    def __init__(self):
        self.username = settings.mail_username
        self.password = settings.mail_password
        self.from_email = settings.mail_from
        self.smtp_server = settings.mail_server
        self.smtp_port = settings.mail_port
        self.use_tls = settings.mail_starttls

    async def send_email(self, to: str, subject: str, html_body: str):
        msg = MIMEMultipart("alternative")
        msg["From"] = self.from_email
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))
        await aiosmtplib.send(
            message=msg,
            hostname=self.smtp_server,
            port=self.smtp_port,
            username=self.username,
            password=self.password,
            start_tls=self.use_tls,
        )

email_sender = EmailSender()