from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from lawfirm_os_orchestrator.commands.classify_exception import run
from lawfirm_os_orchestrator.substrate.reader import PathSubstrateClient

ROOT = Path(__file__).resolve().parents[1]


def args(tmp_path, input_path=None, lake_mode="disabled"):
    return SimpleNamespace(
        input=str(input_path or ROOT / "examples" / "synthetic_exception_event.json"),
        substrate=str(ROOT / "tests" / "fixtures" / "substrate"),
        ledger_dir=str(tmp_path / "ledger"),
        packet_out=str(tmp_path / "runs"),
        lake_mode=lake_mode,
        stdout="json",
    )


def test_end_to_end_disabled_lake(tmp_path):
    code, summary = run(args(tmp_path))
    assert code == 0
    assert summary["status"] == "ok"
    assert Path(summary["ledger_path"]).exists()
    assert (Path(summary["evidence_packet_path"]) / "manifest.json").exists()
    assert summary["manifest_hash"].startswith("sha256:")


def test_reject_real_data_flags(tmp_path):
    bad = json.loads((ROOT / "examples" / "synthetic_exception_event.json").read_text())
    bad["contains_real_client_data"] = True
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    code, summary = run(args(tmp_path, input_path=path))
    assert code == 2
    assert summary["status"] == "failed_validation"


def test_dry_run_lake_writes_receipt(tmp_path):
    code, summary = run(args(tmp_path, lake_mode="dry-run"))
    assert code == 0
    packet_dir = Path(summary["evidence_packet_path"])
    assert (packet_dir / "ingest_request.json").exists()
    assert (packet_dir / "ingest_receipt.json").exists()


def test_substrate_client_has_no_write_methods():
    client = PathSubstrateClient(ROOT / "tests" / "fixtures" / "substrate")
    forbidden = [name for name in dir(client) if name.startswith(("write", "update", "delete", "mutate"))]
    assert forbidden == []
