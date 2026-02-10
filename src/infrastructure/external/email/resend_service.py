"""Resend email service implementation."""

from typing import Optional

import resend

from src.core.config.settings import settings
from src.core.exceptions import ExternalServiceError
from src.domain.interfaces.services import IEmailService


class ResendEmailService(IEmailService):
    """Email service implementation using Resend SDK."""

    def __init__(self):
        if not settings.resend_api_key:
            raise ValueError("RESEND_API_KEY is required")
        resend.api_key = settings.resend_api_key
        self.from_email = settings.email_from

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """Send an email using Resend."""
        try:
            params = resend.Emails.SendParams(
                from_=self.from_email,
                to=[to],
                subject=subject,
                text=body,
                html=html_body if html_body else None,
            )
            resend.Emails.send(params)
            return True

        except Exception as e:
            raise ExternalServiceError(
                service_name="Resend Email",
                message=f"Failed to send email: {str(e)}",
            ) from e

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
        reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"

        body = f"""
You requested to reset your Nevo password.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
The Nevo Team
        """
        html_body = f"""
<html>
<body>
<h2>Reset Your Nevo Password</h2>
<p>You requested to reset your Nevo password.</p>
<p><a href="{reset_link}">Click here to reset your password</a></p>
<p>This link will expire in 1 hour.</p>
<p>If you didn't request this, please ignore this email.</p>
<p>Best regards,<br>The Nevo Team</p>
</body>
</html>
        """
        return await self.send_email(to, subject, body, html_body)

    async def send_verification_email(
        self,
        to: str,
        verification_token: str,
    ) -> bool:
        """Send email verification link."""
        subject = "Verify Your Nevo Email"
        verify_link = f"{settings.frontend_url}/verify-email?token={verification_token}"

        body = f"""
Please verify your email address to complete your Nevo registration.

Click the link below to verify:
{verify_link}

This link will expire in 24 hours.

Best regards,
The Nevo Team
        """
        html_body = f"""
<html>
<body>
<h2>Verify Your Nevo Email</h2>
<p>Please verify your email address to complete your Nevo registration.</p>
<p><a href="{verify_link}">Click here to verify your email</a></p>
<p>This link will expire in 24 hours.</p>
<p>Best regards,<br>The Nevo Team</p>
</body>
</html>
        """
        return await self.send_email(to, subject, body, html_body)
