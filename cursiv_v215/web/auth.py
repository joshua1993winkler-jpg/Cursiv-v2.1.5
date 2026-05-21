"""
Auth helpers — bcrypt password hashing + JWT session tokens.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

_PWD = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secret pulled from env so it's not in the repo
_SECRET = os.environ.get("CURSIV_BOARD_SECRET", "change-me-in-production-env")
_ALG    = "HS256"
_TTL_H  = 72   # token lifetime in hours


def hash_password(plain: str) -> str:
    return _PWD.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _PWD.verify(plain, hashed)


def create_token(user_id: str, username: str) -> str:
    exp = datetime.utcnow() + timedelta(hours=_TTL_H)
    return jwt.encode(
        {"sub": user_id, "username": username, "exp": exp},
        _SECRET, algorithm=_ALG,
    )


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, _SECRET, algorithms=[_ALG])
    except JWTError:
        return None
