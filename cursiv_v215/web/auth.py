"""
Auth helpers — bcrypt password hashing + JWT session tokens.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta

import jwt

_SECRET = os.environ.get("CURSIV_BOARD_SECRET", "change-me-in-production-env")
_ALG    = "HS256"
_TTL_H  = 72


def hash_password(plain: str) -> str:
    salt = secrets.token_hex(16)
    dk   = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 260_000)
    return salt + "$" + dk.hex()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        salt, dk_hex = hashed.split("$", 1)
        dk = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 260_000)
        return hmac.compare_digest(dk.hex(), dk_hex)
    except Exception:
        return False


def create_token(user_id: str, username: str) -> str:
    exp = datetime.utcnow() + timedelta(hours=_TTL_H)
    return jwt.encode(
        {"sub": user_id, "username": username, "exp": exp},
        _SECRET, algorithm=_ALG,
    )


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, _SECRET, algorithms=[_ALG])
    except Exception:
        return None
