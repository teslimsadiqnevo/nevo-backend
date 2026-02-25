"""Profile settings schemas."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AccessibilitySettings(BaseModel):
    """Accessibility settings schema."""

    voice_guidance: bool = Field(False, description="Enable voice guidance")
    large_text: bool = Field(False, description="Enable larger text")
    extra_spacing: bool = Field(False, description="Enable extra spacing")


class ProfileSettingsResponse(BaseModel):
    """Response schema for student profile settings."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "student_name": "Lydia Solomon",
                "role": "student",
                "nevo_id": "NEVO-7K3P2",
                "has_pin": True,
                "accessibility": {
                    "voice_guidance": True,
                    "large_text": False,
                    "extra_spacing": False,
                },
            }
        }
    )

    student_name: str = Field(..., description="Student's full name")
    role: str = Field(..., description="User role")
    nevo_id: Optional[str] = Field(None, description="Student's Nevo ID")
    has_pin: bool = Field(..., description="Whether student has set a PIN")
    accessibility: AccessibilitySettings = Field(
        ..., description="Accessibility preferences"
    )


class UpdateAccessibilityRequest(BaseModel):
    """Request schema for updating accessibility settings (all fields optional)."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "voice_guidance": True,
            }
        }
    )

    voice_guidance: Optional[bool] = Field(None, description="Enable voice guidance")
    large_text: Optional[bool] = Field(None, description="Enable larger text")
    extra_spacing: Optional[bool] = Field(None, description="Enable extra spacing")
