"""Profile settings DTOs."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProfileSettingsOutput:
    """Output DTO for student profile settings."""

    student_name: str
    role: str
    nevo_id: Optional[str]
    has_pin: bool
    voice_guidance: bool
    large_text: bool
    extra_spacing: bool


@dataclass(frozen=True)
class UpdateAccessibilityInput:
    """Input DTO for updating accessibility settings."""

    user_id: object  # UUID
    voice_guidance: Optional[bool] = None
    large_text: Optional[bool] = None
    extra_spacing: Optional[bool] = None
