"""Send transactional email via backoffice SMTP settings."""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config.settings import settings
from utils.input_sanitizer import sanitize_string, validate_email

logger = logging.getLogger(__name__)


def send_plain_email(to_email: str, subject: str, body: str) -> bool:
    """
    Send a plain-text email to a single recipient.
    Uses the same SMTP_* settings as monitoring alerts.
    """
    if not settings.SMTP_HOST or not settings.SMTP_FROM_EMAIL:
        logger.warning("SMTP not configured; cannot send email to recipient")
        return False

    to_email = (to_email or "").strip()
    if not validate_email(to_email):
        logger.warning("Invalid recipient email; skipping send")
        return False

    subject = sanitize_string(subject, max_length=200)
    body = sanitize_string(body, max_length=5000)

    msg = MIMEMultipart()
    msg["From"] = settings.SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Transactional email sent to %s (subject=%s)", to_email, subject[:80])
        return True
    except smtplib.SMTPException as e:
        logger.error("SMTP error sending to %s: %s", to_email, e)
        return False
    except Exception as e:
        logger.error("Error sending email to %s: %s", to_email, e, exc_info=True)
        return False
