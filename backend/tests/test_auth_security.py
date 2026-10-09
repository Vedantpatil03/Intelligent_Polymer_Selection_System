import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017")
os.environ.setdefault("AUTH_SECRET_KEY", "test-secret-key-that-is-long-enough")

import jwt
from fastapi import HTTPException
from starlette.requests import Request

from api import auth
from api import routes as app_routes


def make_request(origin: str, scheme: str, host: str = "api.example.com") -> Request:
    return Request(
        {
            "type": "http",
            "headers": [(b"origin", origin.encode())],
            "path": "/",
            "raw_path": b"/",
            "query_string": b"",
            "server": (host, 443 if scheme == "https" else 80),
            "scheme": scheme,
        }
    )


def test_password_hash_is_not_plaintext_and_round_trips():
    password = "Correct Horse Battery Staple"
    password_hash = auth.hash_password(password)

    assert password_hash != password
    assert auth.verify_password(password, password_hash)
    assert not auth.verify_password("wrong password", password_hash)


def test_cross_origin_https_session_cookie_is_credential_compatible(monkeypatch):
    monkeypatch.delenv("COOKIE_SECURE", raising=False)
    monkeypatch.delenv("COOKIE_SAMESITE", raising=False)

    secure, samesite = auth._cookie_settings(
        make_request("https://polyguideai.vercel.app", "https")
    )

    assert secure is True
    assert samesite == "none"


def test_local_http_session_cookie_remains_compatible(monkeypatch):
    monkeypatch.delenv("COOKIE_SECURE", raising=False)
    monkeypatch.delenv("COOKIE_SAMESITE", raising=False)

    secure, samesite = auth._cookie_settings(
        make_request("http://localhost:5173", "http", host="localhost")
    )

    assert secure is False
    assert samesite == "lax"


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


def test_missing_session_is_rejected():
    request = Request(
        {
            "type": "http",
            "headers": [],
            "path": "/applications",
            "raw_path": b"/applications",
            "query_string": b"",
            "server": ("api.example.com", 443),
            "scheme": "https",
        }
    )

    try:
        auth.get_current_user(request)
        assert False, "missing session should be rejected"
    except HTTPException as error:
        assert error.status_code == 401


def test_dashboard_routes_are_protected_by_router_dependency():
    protected_paths = {"/applications", "/polymers", "/properties"}
    registered_paths = {
        route.path
        for route in app_routes.router.routes
        if route.path in protected_paths
    }

    assert registered_paths == protected_paths
    assert any(
        dependency.dependency is auth.get_current_user
        for dependency in app_routes.router.dependencies
    )


def test_history_lookup_scopes_record_to_current_user(monkeypatch):
    expected_user_id = "507f1f77bcf86cd799439011"
    queried = {}

    class History:
        def find_one(self, query):
            queried.update(query)
            return None

    monkeypatch.setattr(app_routes, "history_collection", History())

    try:
        app_routes.get_history_record(
            "507f1f77bcf86cd799439012",
            {"_id": expected_user_id},
        )
        assert False, "a record owned by another user should not be returned"
    except HTTPException as error:
        assert error.status_code == 404

    assert queried["user_id"] == expected_user_id


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
