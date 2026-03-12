"""Waitlist schemas."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


VALID_ROLES = ["student", "teacher", "parent", "school_admin"]


class JoinWaitlistRequest(BaseModel):
    """Request schema for joining the waitlist."""

    name: str = Field(..., min_length=1, max_length=255, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    role: str = Field(..., description="Role: student, teacher, parent, or school_admin")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Teslim Adewale",
                "email": "teslim@example.com",
                "role": "teacher",
            }
        }


class JoinWaitlistResponse(BaseModel):
    """Response schema for joining the waitlist."""

    message: str
    waitlist_id: str


class WaitlistEntrySchema(BaseModel):
    """Schema for a waitlist entry."""

    id: str
    name: str
    email: str
    role: str
    email_sent: bool
    created_at: datetime


class WaitlistListResponse(BaseModel):
    """Response schema for listing waitlist entries."""

    entries: List[WaitlistEntrySchema]
    total: int
    by_role: Dict[str, int]
