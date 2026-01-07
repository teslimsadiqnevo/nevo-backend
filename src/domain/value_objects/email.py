"""Email value object."""

import re
from dataclasses import dataclass

from src.core.exceptions import ValidationError


@dataclass(frozen=True)
class Email:
    """Email value object with validation."""

    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValidationError(
                message=f"Invalid email format: {self.value}",
                field="email",
            )

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format."""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def __str__(self) -> str:
        return self.value

    @property
    def domain(self) -> str:
        """Get the email domain."""
        return self.value.split("@")[1]

    @property
    def local_part(self) -> str:
        """Get the local part before @."""
        return self.value.split("@")[0]
