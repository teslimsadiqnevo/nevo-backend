"""Class code generation utilities for teachers."""

import secrets

from src.core.security.nevo_id import NEVO_ID_ALPHABET

CLASS_CODE_LENGTH = 3
CLASS_CODE_PREFIX = "NEVO-CLASS-"


def generate_class_code() -> str:
    """Generate a random class code in format NEVO-CLASS-XXX.

    Uses a 32-character unambiguous alphabet for 3 characters,
    giving ~32,768 possible combinations (32^3).
    """
    suffix = "".join(secrets.choice(NEVO_ID_ALPHABET) for _ in range(CLASS_CODE_LENGTH))
    return f"{CLASS_CODE_PREFIX}{suffix}"
