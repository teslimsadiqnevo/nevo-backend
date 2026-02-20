"""Connection schemas."""

from typing import List, Optional

from pydantic import BaseModel, Field


class SendConnectionRequest(BaseModel):
    """Send connection request schema."""

    class_code: str = Field(
        ..., min_length=1, max_length=20, description="Teacher's class code (e.g. NEVO-CLASS-4K7)"
    )


class SendConnectionResponse(BaseModel):
    """Send connection response schema."""

    connection_id: str
    teacher_name: str
    status: str


class ConnectionTeacherSchema(BaseModel):
    """Teacher info in a connection."""

    connection_id: str
    teacher_name: str
    subject: Optional[str] = None
    created_at: str


class StudentConnectionsResponse(BaseModel):
    """Student connections list response."""

    nevo_id: Optional[str] = None
    pending: List[ConnectionTeacherSchema] = Field(default_factory=list)
    connected: List[ConnectionTeacherSchema] = Field(default_factory=list)


class ClassCodeResponse(BaseModel):
    """Teacher's class code response."""

    class_code: str


class ConnectionStudentSchema(BaseModel):
    """Student info in a connection request."""

    connection_id: str
    student_name: str
    created_at: str


class TeacherRequestsResponse(BaseModel):
    """Teacher's pending connection requests."""

    requests: List[ConnectionStudentSchema] = Field(default_factory=list)


class RespondToRequestRequest(BaseModel):
    """Respond to connection request schema."""

    action: str = Field(
        ..., description="'accept' or 'reject'"
    )


class RespondToRequestResponse(BaseModel):
    """Respond to connection request response."""

    connection_id: str
    status: str
