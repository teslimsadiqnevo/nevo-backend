"""Email endpoints for sending custom emails."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from src.core.exceptions import ExternalServiceError
from src.domain.interfaces.services import IEmailService
from src.presentation.api.v1.dependencies import get_current_active_user, CurrentUser
from src.presentation.api.v1.dependencies.services import get_email_service
from src.presentation.schemas.email import (
    SendEmailRequest,
    SendEmailResponse,
    SendBulkEmailRequest,
    SendBulkEmailResponse,
)

router = APIRouter()


@router.post(
    "/send",
    response_model=SendEmailResponse,
    summary="Send custom email",
    description="""
Send a custom email to a single recipient.

**Use Cases:**
- Welcome emails
- Notification emails
- Custom communications
- Password resets
- Email verifications
- Any other email needs

**Features:**
- Supports plain text and HTML
- Uses Resend service
- Automatic error handling

**Example:**
```json
{
  "to": "user@example.com",
  "subject": "Welcome to Nevo!",
  "body": "Welcome to our platform...",
  "html_body": "<h1>Welcome!</h1><p>Welcome to our platform...</p>"
}
```
    """,
    responses={
        200: {"description": "Email sent successfully"},
        400: {"description": "Invalid request data"},
        500: {"description": "Email service error"},
    }
)
async def send_email(
    request: SendEmailRequest,
    current_user: CurrentUser = Depends(get_current_active_user),
    email_service: IEmailService = Depends(get_email_service),
):
    """
    Send a custom email to a single recipient.
    
    Requires authentication. The email will be sent from the configured sender address.
    """
    try:
        success = await email_service.send_email(
            to=request.to,
            subject=request.subject,
            body=request.body,
            html_body=request.html_body,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send email",
            )

        return SendEmailResponse(
            success=True,
            message="Email sent successfully",
            recipient=request.to,
        )

    except ExternalServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Email service error: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}",
        )


@router.post(
    "/send-bulk",
    response_model=SendBulkEmailResponse,
    summary="Send bulk emails",
    description="""
Send the same email to multiple recipients.

**Use Cases:**
- Newsletter
- Announcements
- Bulk notifications
- Group communications

**Note:** Each email is sent individually. For large lists, consider using a background job.
    """,
    responses={
        200: {"description": "Bulk email operation completed"},
        400: {"description": "Invalid request data"},
    }
)
async def send_bulk_email(
    request: SendBulkEmailRequest,
    current_user: CurrentUser = Depends(get_current_active_user),
    email_service: IEmailService = Depends(get_email_service),
):
    """
    Send the same email to multiple recipients.
    
    Requires authentication. Returns success/failure count.
    """
    if not request.recipients or len(request.recipients) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one recipient is required",
        )

    if len(request.recipients) > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 100 recipients allowed per request",
        )

    success_count = 0
    failed_count = 0
    failed_recipients = []

    for recipient in request.recipients:
        try:
            success = await email_service.send_email(
                to=recipient,
                subject=request.subject,
                body=request.body,
                html_body=request.html_body,
            )

            if success:
                success_count += 1
            else:
                failed_count += 1
                failed_recipients.append(recipient)

        except Exception:
            failed_count += 1
            failed_recipients.append(recipient)

    return SendBulkEmailResponse(
        total=len(request.recipients),
        success_count=success_count,
        failed_count=failed_count,
        failed_recipients=failed_recipients if failed_recipients else None,
    )

