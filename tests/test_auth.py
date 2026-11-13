# tests/test_auth.py
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.database import settings
from app.security import ALGORITHM


def test_signup_success(client):
    resp = client.post(
        "/auth/signup", json={"email": "a@example.com", "password": "password123"}
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == "a@example.com"
    assert "id" in body
    # the password or its hash must never be returned
    assert "password" not in body
    assert "hashed_password" not in body


def test_signup_duplicate_email_returns_409(client):
    payload = {"email": "a@example.com", "password": "password123"}
    client.post("/auth/signup", json=payload)
    resp = client.post("/auth/signup", json=payload)
    assert resp.status_code == 409


def test_signup_email_is_case_insensitive(client):
    client.post("/auth/signup", json={"email": "User@Example.com", "password": "password123"})
    resp = client.post("/auth/login", data={"username": "user@example.com", "password": "password123"})
    assert resp.status_code == 200


def test_signup_rejects_invalid_email(client):
    resp = client.post(
        "/auth/signup", json={"email": "not-an-email", "password": "password123"}
    )
    assert resp.status_code == 422


def test_signup_rejects_short_password(client):
    resp = client.post(
        "/auth/signup", json={"email": "a@example.com", "password": "short"}
    )
    assert resp.status_code == 422


def test_login_success_returns_token(client):
    client.post("/auth/signup", json={"email": "a@example.com", "password": "password123"})
    resp = client.post(
        "/auth/login", data={"username": "a@example.com", "password": "password123"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_returns_401(client):
    client.post("/auth/signup", json={"email": "a@example.com", "password": "password123"})
    resp = client.post(
        "/auth/login", data={"username": "a@example.com", "password": "wrong-password"}
    )
    assert resp.status_code == 401


def test_login_unknown_user_returns_401(client):
    resp = client.post(
        "/auth/login", data={"username": "nobody@example.com", "password": "password123"}
    )
    assert resp.status_code == 401


def test_protected_route_without_token_returns_401(client):
    assert client.get("/tasks").status_code == 401


def test_protected_route_with_garbage_token_returns_401(client):
    resp = client.get("/tasks", headers={"Authorization": "Bearer not.a.real.token"})
    assert resp.status_code == 401


def test_expired_token_is_rejected(client):
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.secret_key,
        algorithm=ALGORITHM,
    )
    resp = client.get("/tasks", headers={"Authorization": f"Bearer {expired}"})
    assert resp.status_code == 401