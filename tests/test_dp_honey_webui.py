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
