"""SMTP email service implementation."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from src.core.config.settings import settings
from src.core.exceptions import ExternalServiceError
from src.domain.interfaces.services import IEmailService


class SMTPEmailService(IEmailService):
    """Email service implementation using SMTP."""

    def __init__(self):
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.user = settings.smtp_user
        self.password = settings.smtp_password
        self.from_email = settings.email_from

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """Send an email."""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to

            # Attach plain text
            msg.attach(MIMEText(body, "plain"))

            # Attach HTML if provided
            if html_body:
                msg.attach(MIMEText(html_body, "html"))

            # Send email
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            raise ExternalServiceError(
                service_name="Email",
                message=f"Failed to send email: {str(e)}",
            )

    async def send_welcome_email(self, to: str, name: str) -> bool:
        """Send welcome email to new user."""
        subject = "Welcome to Nevo!"
        body = f"""
Hello {name},

Welcome to Nevo! We're excited to have you on board.

Nevo is an AI-powered personalized learning platform designed to help every student learn in the way that works best for them.

If you have any questions, feel free to reach out to our support team.

Best regards,
The Nevo Team
        """
        html_body = f"""
<html>
<body>
<h2>Welcome to Nevo!</h2>
<p>Hello {name},</p>
<p>We're excited to have you on board.</p>
<p>Nevo is an AI-powered personalized learning platform designed to help every student learn in the way that works best for them.</p>
<p>If you have any questions, feel free to reach out to our support team.</p>
<p>Best regards,<br>The Nevo Team</p>
</body>
</html>
        """
        return await self.send_email(to, subject, body, html_body)

    async def send_password_reset_email(
        self,
        to: str,
        reset_token: str,
    ) -> bool:
        """Send password reset email."""
        subject = "Reset Your Nevo Password"
        # In production, use actual frontend URL
        reset_link = f"https://app.nevo.com/reset-password?token={reset_token}"

        body = f"""
You requested to reset your Nevo password.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
The Nevo Team
        """
        return await self.send_email(to, subject, body)

    async def send_verification_email(
        self,
        to: str,
        verification_token: str,
    ) -> bool:
        """Send email verification link."""
        subject = "Verify Your Nevo Email"
        # In production, use actual frontend URL
        verify_link = f"https://app.nevo.com/verify-email?token={verification_token}"

        body = f"""
Please verify your email address to complete your Nevo registration.

Click the link below to verify:
{verify_link}

This link will expire in 24 hours.

Best regards,
The Nevo Team
        """
        return await self.send_email(to, subject, body)
