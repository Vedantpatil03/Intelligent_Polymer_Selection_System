import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from fastapi import Depends, HTTPException, Request, Response, status

from database.collections import users_collection


AUTH_COOKIE_NAME = "polyguide_session"
SESSION_TTL_HOURS = int(os.getenv("AUTH_SESSION_TTL_HOURS", "24"))
JWT_ALGORITHM = "HS256"
password_hasher = PasswordHasher()


def _secret() -> str:
    value = os.getenv("AUTH_SECRET_KEY")
    if not value:
        raise RuntimeError("AUTH_SECRET_KEY is not configured on the backend.")
    return value


def _user_response(user: dict[str, Any]) -> dict[str, Any]:
    return {
        "user_id": str(user["_id"]),
        "email": user["email"],
        "display_name": user["display_name"],
        "organization": user.get("organization"),
        "created_at": user.get("created_at"),
    }


def normalize_email(email: str) -> str:
    return email.strip().casefold()


def create_session_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": user_id,
            "iat": now,
            "exp": now + timedelta(hours=SESSION_TTL_HOURS),
            "jti": secrets.token_urlsafe(16),
        },
        _secret(),
        algorithm=JWT_ALGORITHM,
    )


def set_session_cookie(response: Response, user_id: str) -> None:
    response.set_cookie(
        AUTH_COOKIE_NAME,
        create_session_token(user_id),
        max_age=SESSION_TTL_HOURS * 60 * 60,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "false").casefold() == "true",
        samesite=os.getenv("COOKIE_SAMESITE", "lax"),
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(AUTH_COOKIE_NAME, path="/")


def get_current_user(request: Request) -> dict[str, Any]:
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    try:
        payload = jwt.decode(token, _secret(), algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Missing subject")
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session is invalid or expired.",
        )

    from bson import ObjectId

    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=401, detail="Your session is invalid.")

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="Your session is invalid.")
    return user


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError):
        return False


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def public_user(user: dict[str, Any]) -> dict[str, Any]:
    return _user_response(user)
