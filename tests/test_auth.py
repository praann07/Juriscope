import base64

from fastapi.testclient import TestClient

from src.app import app
from src.auth import is_authorized


def _basic(user: str, password: str) -> str:
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    return f"Basic {token}"


def test_is_authorized_accepts_matching_credentials():
    assert is_authorized(_basic("alice", "s3cret"), "alice", "s3cret")


def test_is_authorized_rejects_wrong_password():
    assert not is_authorized(_basic("alice", "wrong"), "alice", "s3cret")


def test_is_authorized_rejects_wrong_username():
    assert not is_authorized(_basic("bob", "s3cret"), "alice", "s3cret")


def test_is_authorized_rejects_missing_or_malformed_headers():
    assert not is_authorized(None, "alice", "s3cret")
    assert not is_authorized("Bearer some-token", "alice", "s3cret")
    assert not is_authorized("Basic !!!not-base64!!!", "alice", "s3cret")
    no_colon = base64.b64encode(b"alicesecret").decode()
    assert not is_authorized(f"Basic {no_colon}", "alice", "s3cret")


def test_protected_route_returns_401_without_credentials(monkeypatch):
    monkeypatch.setenv("JURISCOPE_USERNAME", "alice")
    monkeypatch.setenv("JURISCOPE_PASSWORD", "s3cret")

    response = TestClient(app).get("/sessions/count")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"].startswith("Basic")


def test_protected_route_is_not_rejected_with_valid_credentials(monkeypatch):
    monkeypatch.setenv("JURISCOPE_USERNAME", "alice")
    monkeypatch.setenv("JURISCOPE_PASSWORD", "s3cret")

    # Without the app lifespan running there is no session manager, so the
    # handler itself returns 503. The point is that the login check let it through.
    response = TestClient(app).get(
        "/sessions/count", headers={"Authorization": _basic("alice", "s3cret")}
    )

    assert response.status_code != 401


def test_health_check_stays_public_when_login_is_enabled(monkeypatch):
    monkeypatch.setenv("JURISCOPE_USERNAME", "alice")
    monkeypatch.setenv("JURISCOPE_PASSWORD", "s3cret")

    response = TestClient(app).get("/api/health")

    assert response.status_code == 200


def test_web_page_requires_login_when_enabled(monkeypatch):
    monkeypatch.setenv("JURISCOPE_USERNAME", "alice")
    monkeypatch.setenv("JURISCOPE_PASSWORD", "s3cret")

    response = TestClient(app).get("/")

    assert response.status_code == 401


def test_login_is_not_required_when_credentials_are_not_configured(monkeypatch):
    monkeypatch.delenv("JURISCOPE_USERNAME", raising=False)
    monkeypatch.delenv("JURISCOPE_PASSWORD", raising=False)

    response = TestClient(app).get("/sessions/count")

    assert response.status_code != 401
