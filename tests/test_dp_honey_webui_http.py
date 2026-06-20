"""HTTP smoke tests for the web UI app.

Kept in its own file with a module-level importorskip: if httpx (TestClient's
dependency) is not installed, ONLY these HTTP tests skip — the service-layer
tests in test_dp_honey_webui.py still run.
"""

from __future__ import annotations

import pytest

pytest.importorskip("httpx")


def _client():
    from fastapi.testclient import TestClient

    from detect.dp_honey.webui.app import create_app

    return TestClient(create_app())


def test_http_formats_endpoint_lists_slugs():
    resp = _client().get("/api/formats")
    assert resp.status_code == 200
    assert any(item["slug"] == "github-ghp" for item in resp.json())


def test_http_generate_returns_valid_tokens():
    resp = _client().post(
        "/api/generate",
        json={"source": "format", "format": "github-ghp", "count": 3, "seed": 1},
    )
    assert resp.status_code == 200
    assert len(resp.json()["tokens"]) == 3


def test_http_dphoney_error_maps_to_400():
    resp = _client().post("/api/generate", json={"source": "format", "format": "nope", "count": 1})
    assert resp.status_code == 400
    assert "error" in resp.json()


def test_http_index_serves_html_with_safety_banner():
    resp = _client().get("/")
    assert resp.status_code == 200
    assert "NOT real" in resp.text
