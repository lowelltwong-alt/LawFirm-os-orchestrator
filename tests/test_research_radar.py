from __future__ import annotations

import json
import socket
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from lawfirm_os_orchestrator.discovery.local_import import import_signal, list_signals
from lawfirm_os_orchestrator.discovery.models import DiscoverySignal

ROOT = Path(__file__).resolve().parents[1]


def test_import_valid_json_signal_appends_jsonl(tmp_path):
    out = tmp_path / "signals.jsonl"
    signal = import_signal(ROOT / "examples" / "research_signals" / "example_signal.json", out)
    assert signal.source_hash.startswith("sha256:")
    assert signal.local_only is True
    assert signal.no_network_required is True
    assert signal.may_edit_code is False
    assert signal.may_run_git is False
    stored = list_signals(out)
    assert len(stored) == 1
    assert stored[0]["signal_id"] == signal.signal_id


def test_import_valid_markdown_signal(tmp_path):
    out = tmp_path / "signals.jsonl"
    signal = import_signal(ROOT / "examples" / "research_signals" / "example_note.md", out)
    assert signal.source_kind == "human_note"
    assert signal.title == "Local Evaluator Note"
    assert len(list_signals(out)) == 1


def test_import_rejects_invalid_schema(tmp_path):
    bad = tmp_path / "bad_signal.json"
    bad.write_text(json.dumps({"title": "Missing required fields"}), encoding="utf-8")
    with pytest.raises(ValidationError):
        import_signal(bad, tmp_path / "signals.jsonl")


def test_import_does_not_require_network(monkeypatch, tmp_path):
    def fail_socket(*args, **kwargs):
        raise AssertionError("network access attempted")

    monkeypatch.setattr(socket, "socket", fail_socket)
    signal = import_signal(ROOT / "examples" / "research_signals" / "example_signal.json", tmp_path / "signals.jsonl")
    assert signal.no_network_required is True


def test_import_is_append_only_jsonl(tmp_path):
    out = tmp_path / "signals.jsonl"
    first = import_signal(ROOT / "examples" / "research_signals" / "example_signal.json", out)
    second = import_signal(ROOT / "examples" / "research_signals" / "example_signal.json", out)
    lines = out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert DiscoverySignal.model_validate_json(lines[0]).signal_id == first.signal_id
    assert DiscoverySignal.model_validate_json(lines[1]).signal_id == second.signal_id


def test_research_radar_import_local_cli_outputs_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "lawfirm_os_orchestrator",
            "research-radar",
            "import-local",
            "--input",
            "examples/research_signals/example_signal.json",
            "--out",
            str(tmp_path / "signals.jsonl"),
            "--stdout",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    output = json.loads(completed.stdout)
    assert output["status"] == "ok"
    assert output["proposal_only"] is True
    assert Path(output["out"]).exists()
