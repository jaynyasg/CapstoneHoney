"""Tests for the command-line interface and error mapping (U5)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from detect.dp_honey import get_format, load_model
from detect.dp_honey.__main__ import GENERATE_MAX, build_parser, main
from detect.dp_honey.realism import REPORT_MAX

GOLDEN = Path(__file__).resolve().parent / "fixtures" / "dp_honey" / "golden_model.json"

REQUIRED_SLUGS = [
    "aws-access-key-id",
    "aws-secret-access-key",
    "oauth-bearer",
    "generic-sk",
    "database-password",
    "jwt",
    "ssh-private-key",
    "stripe-sk-live",
    "github-ghp",
]


def test_list_formats_includes_every_slug(capsys):
    assert main(["list-formats"]) == 0
    out = capsys.readouterr().out
    for slug in REQUIRED_SLUGS:
        assert slug in out


def test_preview_corpus_outputs_valid_examples(capsys):
    assert main(["preview-corpus", "--format", "github-ghp", "--count", "3", "--seed", "0"]) == 0
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln]
    assert len(lines) == 3
    spec = get_format("github-ghp")
    assert all(spec.validate(ln) for ln in lines)


def test_train_writes_artifact(tmp_path, capsys):
    out = tmp_path / "m.json"
    rc = main(["train", "--format", "github-ghp", "--out", str(out), "--corpus-size", "20", "--seed", "1"])
    assert rc == 0
    assert out.exists()
    load_model(out)  # must be a loadable, valid artifact


def test_generate_from_format_emits_n_valid_tokens(capsys):
    assert main(["generate", "--format", "github-ghp", "--count", "3", "--seed", "7"]) == 0
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln]
    assert len(lines) == 3
    spec = get_format("github-ghp")
    assert all(spec.validate(ln) for ln in lines)


def test_generate_from_model_emits_valid_tokens(tmp_path, capsys):
    out = tmp_path / "m.json"
    main(["train", "--format", "stripe-sk-live", "--out", str(out), "--corpus-size", "20", "--seed", "1"])
    capsys.readouterr()  # clear
    assert main(["generate", "--model", str(out), "--count", "3", "--seed", "2"]) == 0
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln]
    assert len(lines) == 3
    spec = get_format("stripe-sk-live")
    assert all(spec.validate(ln) for ln in lines)


def test_generate_json_output_is_a_list(capsys):
    assert main(["generate", "--format", "github-ghp", "--count", "4", "--seed", "1", "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list) and len(payload) == 4


def test_inspect_model_shows_fields(capsys):
    assert main(["inspect-model", "--model", str(GOLDEN)]) == 0
    out = capsys.readouterr().out
    assert "aws-access-key-id" in out
    assert "epsilon=" in out
    assert "schema_version" in out
    assert "snapshot_status: OK" in out
    assert "synthetic_only=True" in out


def test_validate_exits_zero_for_valid_artifact(capsys):
    assert main(["validate", "--model", str(GOLDEN)]) == 0


def test_validate_exits_nonzero_for_invalid_artifact(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text("{ not valid json", encoding="utf-8")
    assert main(["validate", "--model", str(bad)]) == 1
    assert "error" in capsys.readouterr().err.lower()


def test_report_emits_all_metrics(capsys):
    assert main(["report", "--format", "github-ghp", "--count", "10", "--seed", "1"]) == 0
    report = json.loads(capsys.readouterr().out)
    for field in ("validity_rate", "char_entropy_bits", "duplicate_rate", "avg_log_likelihood", "debug"):
        assert field in report


def test_unknown_format_exits_nonzero(capsys):
    assert main(["generate", "--format", "not-real", "--count", "1"]) == 1
    assert "error" in capsys.readouterr().err.lower()


def test_existing_output_without_force_exits_nonzero(tmp_path, capsys):
    out = tmp_path / "m.json"
    assert main(["train", "--format", "github-ghp", "--out", str(out), "--corpus-size", "10"]) == 0
    rc = main(["train", "--format", "github-ghp", "--out", str(out), "--corpus-size", "10"])
    assert rc == 1
    assert "error" in capsys.readouterr().err.lower()


def test_oversized_generate_count_exits_before_work(capsys):
    rc = main(["generate", "--format", "github-ghp", "--count", str(GENERATE_MAX + 1)])
    assert rc == 1
    assert str(GENERATE_MAX) in capsys.readouterr().err


def test_oversized_report_count_exits_before_work(capsys):
    rc = main(["report", "--format", "github-ghp", "--count", str(REPORT_MAX + 1)])
    assert rc == 1
    assert str(REPORT_MAX) in capsys.readouterr().err


def test_generate_emits_safety_banner_on_stderr(capsys):
    assert main(["generate", "--format", "github-ghp", "--count", "1", "--seed", "0"]) == 0
    assert "synthetic" in capsys.readouterr().err.lower()


def test_help_text_mentions_synthetic():
    assert "synthetic" in build_parser().format_help().lower()
