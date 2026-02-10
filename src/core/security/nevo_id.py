"""Nevo ID generation utilities."""

import secrets

# 32-character alphabet excluding ambiguous characters: 0/O, 1/I/L
NEVO_ID_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
NEVO_ID_LENGTH = 5
NEVO_ID_PREFIX = "NEVO-"


def generate_nevo_id() -> str:
    """Generate a random Nevo ID in format NEVO-XXXXX.

    Uses a 32-character unambiguous alphabet for 5 characters,
    giving ~33 million possible combinations (32^5 = 33,554,432).
    """
    suffix = "".join(secrets.choice(NEVO_ID_ALPHABET) for _ in range(NEVO_ID_LENGTH))
    return f"{NEVO_ID_PREFIX}{suffix}"
