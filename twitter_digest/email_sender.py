"""Email sender for the Twitter Digest."""

import logging
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

from .config_loader import SmtpConfig

logger = logging.getLogger(__name__)


def send_email(
    subject: str,
    body_text: str,
    recipients: list[str],
    from_address: str,
    smtp_config: SmtpConfig,
    pdf_path: str | None = None,
    pdf_bytes: bytes | None = None,
    pdf_filename: str = "twitter-digest.pdf",
) -> None:
    """
    Send an email with optional PDF attachment.

    Either pdf_path or pdf_bytes should be provided for attachment.
    """
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_address
    msg["To"] = ", ".join(recipients)
    msg.set_content(body_text)

    if pdf_path:
        path = Path(pdf_path)
        if path.exists():
            with open(path, "rb") as f:
                pdf_data = f.read()
            msg.add_attachment(
                pdf_data,
                maintype="application",
                subtype="pdf",
                filename=pdf_filename,
            )
            logger.info(f"Attached PDF from file: {pdf_path}")
    elif pdf_bytes:
        msg.add_attachment(
            pdf_bytes,
            maintype="application",
            subtype="pdf",
            filename=pdf_filename,
        )
        logger.info("Attached PDF from bytes")

    try:
        if smtp_config.use_tls:
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_config.host, smtp_config.port) as server:
                server.starttls(context=context)
                server.login(smtp_config.username, smtp_config.password)
                server.send_message(msg)
        else:
            with smtplib.SMTP_SSL(smtp_config.host, smtp_config.port) as server:
                server.login(smtp_config.username, smtp_config.password)
                server.send_message(msg)

        logger.info(f"Email sent successfully to {recipients}")

    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {e}")
        raise
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise
