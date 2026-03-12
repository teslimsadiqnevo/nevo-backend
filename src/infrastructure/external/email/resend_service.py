"""Resend email service implementation."""

import logging
from typing import Optional

import httpx

from src.core.config.settings import settings
from src.core.exceptions import ExternalServiceError
from src.domain.interfaces.services import IEmailService

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"

# Nevo brand colors
BRAND_PRIMARY = "#6C3CE1"      # Purple - primary brand color
BRAND_DARK = "#1A1A2E"         # Dark navy - headings
BRAND_TEXT = "#4A4A68"          # Muted dark - body text
BRAND_LIGHT_BG = "#F8F6FF"     # Light purple tint - background
BRAND_ACCENT = "#8B5CF6"       # Lighter purple - hover/accent
BRAND_BORDER = "#E8E0FF"       # Very light purple - borders


def _email_wrapper(content: str) -> str:
    """Wrap email content in the branded Nevo template."""
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#F3F0FA;font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color:#F3F0FA;padding:40px 20px;">
<tr><td align="center">
<table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="background-color:#FFFFFF;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(108,60,225,0.08);">

<!-- Header -->
<tr>
<td style="background:linear-gradient(135deg,{BRAND_PRIMARY},{BRAND_ACCENT});padding:36px 40px;text-align:center;">
<h1 style="margin:0;font-size:32px;font-weight:800;color:#FFFFFF;letter-spacing:-0.5px;">Nevo</h1>
<p style="margin:6px 0 0;font-size:13px;color:rgba(255,255,255,0.85);letter-spacing:0.5px;">AI-Powered Personalized Learning</p>
</td>
</tr>

<!-- Body -->
<tr>
<td style="padding:40px 40px 32px;">
{content}
</td>
</tr>

<!-- Footer -->
<tr>
<td style="padding:24px 40px 32px;border-top:1px solid {BRAND_BORDER};text-align:center;">
<p style="margin:0 0 8px;font-size:13px;color:#9CA3AF;">Made with care by the <strong style="color:{BRAND_PRIMARY};">Nevo</strong> team</p>
<p style="margin:0;font-size:12px;color:#C0C0D0;">&copy; 2026 Nevo Learning. All rights reserved.</p>
</td>
</tr>

</table>
</td></tr>
</table>
</body>
</html>"""


class ResendEmailService(IEmailService):
    """Email service implementation using Resend HTTP API."""

    def __init__(self):
        if not settings.resend_api_key:
            raise ValueError("RESEND_API_KEY is required")
        self.api_key = settings.resend_api_key
        self.from_email = settings.email_from

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """Send an email using Resend HTTP API (fully async)."""
        try:
            payload = {
                "from": self.from_email,
                "to": [to],
                "subject": subject,
                "text": body,
            }
            if html_body:
                payload["html"] = html_body

            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=10,
                )

            if resp.status_code >= 400:
                raise Exception(f"Resend API error {resp.status_code}: {resp.text}")

            result = resp.json()
            logger.info(f"Email sent to {to}: {result}")
            return True

        except Exception as e:
            raise ExternalServiceError(
                service_name="Resend Email",
                message=f"Failed to send email: {str(e)}",
            ) from e

    async def send_welcome_email(self, to: str, name: str) -> bool:
        """Send welcome email to new user."""
        subject = "Welcome to Nevo!"
        body = (
            f"Hello {name},\n\n"
            "Welcome to Nevo! We're excited to have you on board.\n\n"
            "Nevo is an AI-powered personalized learning platform designed to help "
            "every student learn in the way that works best for them.\n\n"
            "If you have any questions, feel free to reach out to our support team.\n\n"
            "Best regards,\nThe Nevo Team"
        )
        html_body = _email_wrapper(f"""\
<h2 style="margin:0 0 20px;font-size:24px;font-weight:700;color:{BRAND_DARK};">Welcome to Nevo!</h2>
<p style="margin:0 0 16px;font-size:16px;line-height:1.6;color:{BRAND_TEXT};">Hello <strong style="color:{BRAND_DARK};">{name}</strong>,</p>
<p style="margin:0 0 16px;font-size:16px;line-height:1.6;color:{BRAND_TEXT};">We're thrilled to have you on board! <strong>Nevo</strong> is an AI-powered personalized learning platform designed to help every student learn in the way that works best for them.</p>
<div style="background:{BRAND_LIGHT_BG};border-left:4px solid {BRAND_PRIMARY};border-radius:8px;padding:20px 24px;margin:24px 0;">
<p style="margin:0;font-size:15px;line-height:1.6;color:{BRAND_TEXT};">Your journey with personalized learning starts now. We're here to support you every step of the way.</p>
</div>
<p style="margin:0 0 16px;font-size:16px;line-height:1.6;color:{BRAND_TEXT};">If you have any questions, feel free to reach out to our support team.</p>
<p style="margin:24px 0 0;font-size:15px;color:{BRAND_TEXT};">Best regards,<br><strong style="color:{BRAND_DARK};">The Nevo Team</strong></p>""")
        return await self.send_email(to, subject, body, html_body)

    async def send_password_reset_email(
        self,
        to: str,
        reset_token: str,
    ) -> bool:
        """Send password reset email."""
        subject = "Reset Your Nevo Password"
        reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"

        body = (
            "You requested to reset your Nevo password.\n\n"
            f"Click the link below to reset your password:\n{reset_link}\n\n"
            "This link will expire in 1 hour.\n\n"
            "If you didn't request this, please ignore this email.\n\n"
            "Best regards,\nThe Nevo Team"
        )
        html_body = _email_wrapper(f"""\
<h2 style="margin:0 0 20px;font-size:24px;font-weight:700;color:{BRAND_DARK};">Reset Your Password</h2>
<p style="margin:0 0 16px;font-size:16px;line-height:1.6;color:{BRAND_TEXT};">You requested to reset your Nevo password. Click the button below to set a new one:</p>
<div style="text-align:center;margin:32px 0;">
<a href="{reset_link}" style="display:inline-block;background:{BRAND_PRIMARY};color:#FFFFFF;font-size:16px;font-weight:700;text-decoration:none;padding:14px 40px;border-radius:8px;">Reset Password</a>
</div>
<div style="background:{BRAND_LIGHT_BG};border-radius:8px;padding:16px 24px;margin:24px 0;">
<p style="margin:0;font-size:14px;color:{BRAND_TEXT};">This link will expire in <strong>1 hour</strong>. If you didn't request this, you can safely ignore this email.</p>
</div>
<p style="margin:24px 0 0;font-size:15px;color:{BRAND_TEXT};">Best regards,<br><strong style="color:{BRAND_DARK};">The Nevo Team</strong></p>""")
        return await self.send_email(to, subject, body, html_body)

    async def send_verification_email(
        self,
        to: str,
        verification_token: str,
    ) -> bool:
        """Send email verification link."""
        subject = "Verify Your Nevo Email"
        verify_link = f"{settings.frontend_url}/verify-email?token={verification_token}"

        body = (
            "Please verify your email address to complete your Nevo registration.\n\n"
            f"Click the link below to verify:\n{verify_link}\n\n"
            "This link will expire in 24 hours.\n\n"
            "Best regards,\nThe Nevo Team"
        )
        html_body = _email_wrapper(f"""\
<h2 style="margin:0 0 20px;font-size:24px;font-weight:700;color:{BRAND_DARK};">Verify Your Email</h2>
<p style="margin:0 0 16px;font-size:16px;line-height:1.6;color:{BRAND_TEXT};">Please verify your email address to complete your Nevo registration:</p>
<div style="text-align:center;margin:32px 0;">
<a href="{verify_link}" style="display:inline-block;background:{BRAND_PRIMARY};color:#FFFFFF;font-size:16px;font-weight:700;text-decoration:none;padding:14px 40px;border-radius:8px;">Verify Email</a>
</div>
<div style="background:{BRAND_LIGHT_BG};border-radius:8px;padding:16px 24px;margin:24px 0;">
<p style="margin:0;font-size:14px;color:{BRAND_TEXT};">This link will expire in <strong>24 hours</strong>.</p>
</div>
<p style="margin:24px 0 0;font-size:15px;color:{BRAND_TEXT};">Best regards,<br><strong style="color:{BRAND_DARK};">The Nevo Team</strong></p>""")
        return await self.send_email(to, subject, body, html_body)

    async def send_waitlist_confirmation(self, to: str, name: str) -> bool:
        """Send waitlist confirmation email."""
        subject = "You're on the Nevo waitlist!"
        body = (
            f"Hi {name},\n\n"
            "Thanks for joining the Nevo waitlist! We're building an AI-powered "
            "personalized learning platform designed to help every student learn "
            "in the way that works best for them.\n\n"
            "You're now on the list, and we'll reach out soon with updates and "
            "early access information.\n\n"
            "Best regards,\nThe Nevo Team"
        )
        html_body = _email_wrapper(f"""\
<h2 style="margin:0 0 20px;font-size:24px;font-weight:700;color:{BRAND_DARK};">You're on the list!</h2>
<p style="margin:0 0 16px;font-size:16px;line-height:1.6;color:{BRAND_TEXT};">Hi <strong style="color:{BRAND_DARK};">{name}</strong>,</p>
<p style="margin:0 0 16px;font-size:16px;line-height:1.6;color:{BRAND_TEXT};">Thanks for joining the <strong style="color:{BRAND_PRIMARY};">Nevo</strong> waitlist! We're building an AI-powered personalized learning platform designed to help every student learn in the way that works best for them.</p>
<div style="background:{BRAND_LIGHT_BG};border-left:4px solid {BRAND_PRIMARY};border-radius:8px;padding:20px 24px;margin:24px 0;">
<p style="margin:0;font-size:15px;line-height:1.6;color:{BRAND_TEXT};">You're now on the list, and we'll reach out soon with <strong style="color:{BRAND_DARK};">updates and early access information</strong>.</p>
</div>
<p style="margin:0 0 16px;font-size:16px;line-height:1.6;color:{BRAND_TEXT};">We can't wait to have you experience what personalized learning truly feels like.</p>
<p style="margin:24px 0 0;font-size:15px;color:{BRAND_TEXT};">Best regards,<br><strong style="color:{BRAND_DARK};">The Nevo Team</strong></p>""")
        return await self.send_email(to, subject, body, html_body)
