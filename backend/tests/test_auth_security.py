import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("AUTH_SECRET_KEY", "test-secret-key-that-is-long-enough")

import jwt
from fastapi import HTTPException
from starlette.requests import Request

from api import auth


def test_password_hash_is_not_plaintext_and_round_trips():
    password = "Correct Horse Battery Staple"
    password_hash = auth.hash_password(password)

    assert password_hash != password
    assert auth.verify_password(password, password_hash)
    assert not auth.verify_password("wrong password", password_hash)


def test_expired_token_is_rejected(monkeypatch):
    token = jwt.encode(
        {
            "sub": "507f1f77bcf86cd799439011",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        "test-secret-key-that-is-long-enough",
        algorithm="HS256",
    )
    request = Request(
        {
            "type": "http",
            "headers": [(b"cookie", f"polyguide_session={token}".encode())],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 1234),
            "scheme": "http",
        }
    )

    monkeypatch.setattr(auth, "users_collection", type("Users", (), {"find_one": lambda *_: None})())

    try:
        auth.get_current_user(request)
        assert False, "expired token should be rejected"
    except HTTPException as error:
        assert error.status_code == 401


def test_current_user_lookup_uses_token_subject(monkeypatch):
    expected = {
        "_id": "507f1f77bcf86cd799439011",
        "email": "user@example.com",
        "display_name": "User",
    }
    token = auth.create_session_token(expected["_id"])
    request = Request(
        {
            "type": "http",
            "headers": [(b"cookie", f"polyguide_session={token}".encode())],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 1234),
            "scheme": "http",
        }
    )

    class Users:
        def find_one(self, query):
            assert query["_id"].binary.hex() == expected["_id"]
            return expected

    monkeypatch.setattr(auth, "users_collection", Users())
    assert auth.get_current_user(request) == expected
