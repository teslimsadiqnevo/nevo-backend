"""Email schemas."""

from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class SendEmailRequest(BaseModel):
    """Request schema for sending a single email."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "to": "user@example.com",
                "subject": "Welcome to Nevo!",
                "body": "Welcome to our platform. We're excited to have you!",
                "html_body": "<h1>Welcome to Nevo!</h1><p>Welcome to our platform. We're excited to have you!</p>"
            }
        }
    )

    to: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject")
    body: str = Field(..., min_length=1, description="Plain text email body")
    html_body: Optional[str] = Field(
        None,
        description="HTML email body (optional, if not provided, plain text will be used)"
    )


class SendEmailResponse(BaseModel):
    """Response schema for email sending."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Email sent successfully",
                "recipient": "user@example.com"
            }
        }
    )

    success: bool = Field(..., description="Whether the email was sent successfully")
    message: str = Field(..., description="Status message")
    recipient: str = Field(..., description="Recipient email address")


class SendBulkEmailRequest(BaseModel):
    """Request schema for sending bulk emails."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "recipients": ["user1@example.com", "user2@example.com"],
                "subject": "Important Announcement",
                "body": "This is an important announcement...",
                "html_body": "<h1>Important Announcement</h1><p>This is an important announcement...</p>"
            }
        }
    )

    recipients: List[EmailStr] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of recipient email addresses (max 100)"
    )
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject")
    body: str = Field(..., min_length=1, description="Plain text email body")
    html_body: Optional[str] = Field(
        None,
        description="HTML email body (optional)"
    )


class SendBulkEmailResponse(BaseModel):
    """Response schema for bulk email sending."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 10,
                "success_count": 9,
                "failed_count": 1,
                "failed_recipients": ["invalid@example.com"]
            }
        }
    )

    total: int = Field(..., description="Total number of recipients")
    success_count: int = Field(..., description="Number of successfully sent emails")
    failed_count: int = Field(..., description="Number of failed emails")
    failed_recipients: Optional[List[str]] = Field(
        None,
        description="List of email addresses that failed (if any)"
    )

