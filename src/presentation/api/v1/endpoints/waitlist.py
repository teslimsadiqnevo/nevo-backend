"""Waitlist endpoints - Public signup and admin listing."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.core.config.constants import UserRole
from src.domain.entities.waitlist import WaitlistEntry
from src.domain.interfaces.services import IEmailService
from src.application.common.unit_of_work import IUnitOfWork
from src.presentation.api.v1.dependencies import get_uow, require_role
from src.presentation.api.v1.dependencies.services import get_email_service
from src.presentation.schemas.waitlist import (
    VALID_ROLES,
    JoinWaitlistRequest,
    JoinWaitlistResponse,
    WaitlistEntrySchema,
    WaitlistListResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/join",
    response_model=JoinWaitlistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Join the Nevo waitlist",
)
async def join_waitlist(
    request: JoinWaitlistRequest,
    uow: IUnitOfWork = Depends(get_uow),
    email_service: IEmailService = Depends(get_email_service),
):
    """Join the Nevo waitlist. Public endpoint -- no auth required."""
    # Validate role
    if request.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}",
        )

    async with uow:
        # Check for duplicate email
        existing = await uow.waitlist.get_by_email(request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You're already on the list.",
            )

        # Create waitlist entry
        entry = WaitlistEntry(
            name=request.name,
            email=request.email,
            role=request.role,
        )
        created = await uow.waitlist.create(entry)
        await uow.commit()

    # Send confirmation email (outside transaction -- don't fail signup if email fails)
    try:
        await email_service.send_waitlist_confirmation(
            to=request.email,
            name=request.name,
        )
    except Exception as e:
        logger.warning(f"Failed to send waitlist confirmation email to {request.email}: {e}")

    return JoinWaitlistResponse(
        message="You're on the Nevo waitlist! Check your email.",
        waitlist_id=str(created.id),
    )


@router.get(
    "/entries",
    response_model=WaitlistListResponse,
    dependencies=[Depends(require_role([UserRole.SCHOOL_ADMIN, UserRole.SUPER_ADMIN]))],
    summary="List waitlist entries (admin only)",
)
async def list_waitlist_entries(
    role: Optional[str] = Query(None, description="Filter by role"),
    limit: int = Query(100, ge=1, le=1000, description="Max entries to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    uow: IUnitOfWork = Depends(get_uow),
):
    """List all waitlist entries. Admin-only endpoint."""
    async with uow:
        entries = await uow.waitlist.list_all(limit=limit, offset=offset, role=role)
        total = await uow.waitlist.count()
        by_role = await uow.waitlist.count_by_role()

    return WaitlistListResponse(
        entries=[
            WaitlistEntrySchema(
                id=str(e.id),
                name=e.name,
                email=e.email,
                role=e.role,
                created_at=e.created_at,
            )
            for e in entries
        ],
        total=total,
        by_role=by_role,
    )
