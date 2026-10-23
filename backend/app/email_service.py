"""SMTP email sending service (provider-independent)."""
import logging
import smtplib
from email.message import EmailMessage
from app.config import (SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD,
                        SMTP_FROM_EMAIL)

log = logging.getLogger('fnds.email')


class EmailNotConfiguredError(RuntimeError):
    pass


def smtp_configured() -> bool:
    return bool(SMTP_HOST and SMTP_FROM_EMAIL)


def send_email(*, to_email: str, subject: str, body: str) -> None:
    """Send a plain-text email. Raises on misconfiguration or delivery failure."""
    if not smtp_configured():
        raise EmailNotConfiguredError('SMTP is not configured (SMTP_HOST/SMTP_FROM_EMAIL missing).')
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SMTP_FROM_EMAIL
    msg['To'] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            try:
                server.starttls()
            except smtplib.SMTPException:
                pass  # some local dev relays do not support STARTTLS
            if SMTP_USERNAME:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as exc:
        # Log the actual server-side problem WITHOUT leaking credentials/tokens.
        log.error('SMTP delivery to user failed: %s', exc)
        raise


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    send_email(
        to_email=to_email,
        subject='Reset your FNDS password',
        body=(
            'We received a request to reset the password for your FNDS account.\n\n'
            f'Reset link (expires in 1 hour, single-use):\n{reset_link}\n\n'
            'If you did not request this, you can ignore this email.'
        ),
    )
