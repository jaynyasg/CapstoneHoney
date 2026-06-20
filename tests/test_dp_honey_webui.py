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


def test_run_generate_from_format_is_valid_and_deterministic():
    params = {"source": "format", "format": "github-ghp", "count": 4, "seed": 7, "train_seed": 3}
    a = service.run_generate(params)
    b = service.run_generate(params)
    assert a["tokens"] == b["tokens"]
    assert len(a["tokens"]) == 4
    spec = get_format("github-ghp")
    assert all(spec.validate(t) for t in a["tokens"])
    assert a["safety"]["provider_valid"] is False


def test_run_generate_oversized_count_rejected():
    with pytest.raises(CountLimitError):
        service.run_generate({"source": "format", "format": "github-ghp", "count": 10_001})


def test_run_report_has_metrics():
    report = service.run_report({"source": "format", "format": "github-ghp", "count": 20, "seed": 1})
    for field in ("validity_rate", "char_entropy_bits", "duplicate_rate", "avg_log_likelihood", "debug"):
        assert field in report


def test_run_report_oversized_count_rejected():
    with pytest.raises(CountLimitError):
        service.run_report({"source": "format", "format": "github-ghp", "count": 5001})


def test_run_generate_from_golden_fixture_model():
    out = service.run_generate({"source": "model", "model": service.GOLDEN_NAME, "count": 3, "seed": 1})
    assert len(out["tokens"]) == 3
    spec = get_format("aws-access-key-id")
    assert all(spec.validate(t) for t in out["tokens"])
