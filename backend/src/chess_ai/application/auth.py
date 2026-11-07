"""Authentication primitives used by the HTTP API."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
import secrets
import time

PASSWORD_ITERATIONS = 600_000
TOKEN_TTL_SECONDS = 60 * 60 * 24


def hash_password(password: str) -> str:
    """Hash a password with a per-password salt using PBKDF2-HMAC-SHA256."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${_encode(salt)}${_encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    """Verify a password hash without exposing timing information."""
    try:
        algorithm, iterations, salt, expected = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            _decode(salt),
            int(iterations),
        )
    except (ValueError, TypeError, binascii.Error, UnicodeError):
        return False
    return hmac.compare_digest(actual, _decode(expected))


def create_access_token(user_id: str, secret: str, expires_in: int = TOKEN_TTL_SECONDS) -> str:
    """Create a compact, signed bearer token."""
    payload = {"sub": user_id, "exp": int(time.time()) + expires_in}
    encoded_payload = _encode(json.dumps(payload, separators=(",", ":")).encode())
    signature = hmac.new(secret.encode(), encoded_payload.encode(), hashlib.sha256).digest()
    return f"{encoded_payload}.{_encode(signature)}"


def get_user_id_from_token(token: str, secret: str) -> str | None:
    """Validate a bearer token and return its subject."""
    try:
        encoded_payload, encoded_signature = token.split(".")
        expected = hmac.new(secret.encode(), encoded_payload.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _decode(encoded_signature)):
            return None
        payload = json.loads(_decode(encoded_payload))
        if not isinstance(payload, dict) or int(payload["exp"]) < int(time.time()):
            return None
        user_id = payload["sub"]
        return user_id if isinstance(user_id, str) and user_id else None
    except (
        ValueError,
        TypeError,
        KeyError,
        json.JSONDecodeError,
        binascii.Error,
        UnicodeError,
        OverflowError,
    ):
        return None


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
