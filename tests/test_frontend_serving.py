from fastapi.testclient import TestClient

import src.app as app_module
from src.app import app


def _build_fake_frontend(tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<html><body>Juriscope UI</body></html>", encoding="utf-8")
    (dist / "assets" / "app.js").write_text("console.log('hi');", encoding="utf-8")
    return dist


def test_health_endpoint_returns_json(monkeypatch):
    monkeypatch.delenv("JURISCOPE_USERNAME", raising=False)
    monkeypatch.delenv("JURISCOPE_PASSWORD", raising=False)

    response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_root_serves_index_html_when_frontend_is_built(tmp_path, monkeypatch):
    monkeypatch.delenv("JURISCOPE_USERNAME", raising=False)
    monkeypatch.delenv("JURISCOPE_PASSWORD", raising=False)
    monkeypatch.setattr(app_module, "FRONTEND_DIST", _build_fake_frontend(tmp_path))

    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert "Juriscope UI" in response.text


def test_built_asset_is_served(tmp_path, monkeypatch):
    monkeypatch.delenv("JURISCOPE_USERNAME", raising=False)
    monkeypatch.delenv("JURISCOPE_PASSWORD", raising=False)
    monkeypatch.setattr(app_module, "FRONTEND_DIST", _build_fake_frontend(tmp_path))

    response = TestClient(app).get("/assets/app.js")

    assert response.status_code == 200
    assert "console.log" in response.text


def test_unknown_client_route_falls_back_to_index_html(tmp_path, monkeypatch):
    monkeypatch.delenv("JURISCOPE_USERNAME", raising=False)
    monkeypatch.delenv("JURISCOPE_PASSWORD", raising=False)
    monkeypatch.setattr(app_module, "FRONTEND_DIST", _build_fake_frontend(tmp_path))

    response = TestClient(app).get("/some/client/route")

    assert response.status_code == 200
    assert "Juriscope UI" in response.text


def test_files_outside_the_build_folder_are_not_served(tmp_path, monkeypatch):
    monkeypatch.delenv("JURISCOPE_USERNAME", raising=False)
    monkeypatch.delenv("JURISCOPE_PASSWORD", raising=False)
    dist = _build_fake_frontend(tmp_path)
    secret = tmp_path / "secret.txt"
    secret.write_text("do not leak", encoding="utf-8")
    monkeypatch.setattr(app_module, "FRONTEND_DIST", dist)

    response = TestClient(app).get("/..%2Fsecret.txt")

    assert "do not leak" not in response.text
    assert "Juriscope UI" in response.text


def test_unknown_api_path_is_404_not_index_html(tmp_path, monkeypatch):
    monkeypatch.delenv("JURISCOPE_USERNAME", raising=False)
    monkeypatch.delenv("JURISCOPE_PASSWORD", raising=False)
    monkeypatch.setattr(app_module, "FRONTEND_DIST", _build_fake_frontend(tmp_path))

    response = TestClient(app).get("/api/does-not-exist")

    assert response.status_code == 404


def test_api_routes_still_win_over_the_frontend_fallback(tmp_path, monkeypatch):
    monkeypatch.delenv("JURISCOPE_USERNAME", raising=False)
    monkeypatch.delenv("JURISCOPE_PASSWORD", raising=False)
    monkeypatch.setattr(app_module, "FRONTEND_DIST", _build_fake_frontend(tmp_path))

    response = TestClient(app).get("/docs")

    assert response.status_code == 200
    assert "Juriscope UI" not in response.text


def test_login_protects_the_frontend_when_enabled(tmp_path, monkeypatch):
    monkeypatch.setenv("JURISCOPE_USERNAME", "alice")
    monkeypatch.setenv("JURISCOPE_PASSWORD", "s3cret")
    monkeypatch.setattr(app_module, "FRONTEND_DIST", _build_fake_frontend(tmp_path))

    response = TestClient(app).get("/assets/app.js")

    assert response.status_code == 401
