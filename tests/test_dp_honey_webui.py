"""Tests for the DP-HONEY web UI service layer (no HTTP)."""

from __future__ import annotations

import pytest

from detect.dp_honey.webui import service
from detect.dp_honey.webui.service import InvalidModelName


@pytest.mark.parametrize("bad", ["../secret", "a/b", "a\\b", "..", "", "name with space", "/abs"])
def test_resolve_model_ref_rejects_unsafe_names(bad, tmp_path):
    with pytest.raises(InvalidModelName):
        service.resolve_model_ref(bad, models_dir=tmp_path)


def test_resolve_model_ref_maps_safe_name_into_models_dir(tmp_path):
    ref = service.resolve_model_ref("my-model", models_dir=tmp_path)
    assert ref == tmp_path / "my-model.json"


def test_resolve_model_ref_maps_golden_label_to_fixture():
    ref = service.resolve_model_ref(service.GOLDEN_NAME)
    assert ref.name == "golden_model.json"
    assert "fixtures" in ref.parts


from detect.dp_honey import get_format
from detect.dp_honey.errors import CountLimitError


def test_list_formats_payload_has_all_slugs_and_safety():
    payload = service.list_formats_payload()
    slugs = {item["slug"] for item in payload}
    assert "github-ghp" in slugs and "aws-access-key-id" in slugs
    assert len(slugs) == 9
    for item in payload:
        assert item["safety_note"]
        assert item["provider_valid"] is False


def test_preview_corpus_returns_valid_examples():
    examples = service.preview_corpus("github-ghp", count=3, seed=0)
    assert len(examples) == 3
    spec = get_format("github-ghp")
    assert all(spec.validate(e) for e in examples)


def test_preview_corpus_rejects_oversized_count():
    with pytest.raises(CountLimitError):
        service.preview_corpus("github-ghp", count=10_001, seed=0)
