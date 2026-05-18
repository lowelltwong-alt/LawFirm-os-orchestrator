from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from lawfirm_os_orchestrator.commands.classify_exception import run
from lawfirm_os_orchestrator.evidence.packet import packet_content_hash
from lawfirm_os_orchestrator.substrate.reader import PathSubstrateClient
from lawfirm_os_orchestrator.util.hashing import sha256_file
from lawfirm_os_orchestrator.util.json_io import read_json

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


def test_final_packet_hash_and_manifest_are_fresh_after_lake_handoff(tmp_path):
    code, summary = run(args(tmp_path, lake_mode="dry-run"))
    assert code == 0
    packet_dir = Path(summary["evidence_packet_path"])
    packet_path = packet_dir / "packet.json"
    manifest_path = packet_dir / "manifest.json"
    packet = read_json(packet_path)
    manifest = read_json(manifest_path)

    assert "lake_handoff" in packet
    assert packet["packet_hash"] == packet_content_hash(packet)
    assert manifest["packet_hash"] == packet["packet_hash"]
    assert manifest["files"]["packet.json"] == sha256_file(packet_path)
    assert "stdout_summary.json" in manifest["files"]
    assert manifest["files"]["stdout_summary.json"] == sha256_file(packet_dir / "stdout_summary.json")


def test_substrate_client_has_no_write_methods():
    client = PathSubstrateClient(ROOT / "tests" / "fixtures" / "substrate")
    forbidden = [name for name in dir(client) if name.startswith(("write", "update", "delete", "mutate"))]
    assert forbidden == []


def test_fixture_substrate_is_allowed_but_still_records_contract_lock():
    snapshot = PathSubstrateClient(ROOT / "tests" / "fixtures" / "substrate").load_snapshot()
    expected_lock = read_json(ROOT / "contracts.lock.json")

    assert snapshot.contract_lock.contract_repo == "LawFirm-os-semantic-substrate"
    assert snapshot.contract_lock.contract_sha == expected_lock["contract_sha"]
    assert snapshot.routes[0].destination_loop == "retrieval_tuning"
    assert snapshot.routes[0].allowed_follow_on_families == [
        "pressure-vector",
        "adaptation-proposal",
        "opportunity-object",
    ]


def test_non_fixture_substrate_without_git_checkout_fails_closed(tmp_path):
    substrate = tmp_path / "LawFirm-os-semantic-substrate"
    shutil.copytree(ROOT / "tests" / "fixtures" / "substrate", substrate)

    with pytest.raises(ValueError, match="not a git checkout"):
        PathSubstrateClient(substrate).load_snapshot()


def test_wrong_substrate_git_sha_fails_closed(tmp_path):
    substrate = tmp_path / "LawFirm-os-semantic-substrate"
    shutil.copytree(ROOT / "tests" / "fixtures" / "substrate", substrate)
    git_dir = substrate / ".git"
    (git_dir / "refs" / "heads").mkdir(parents=True)
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (git_dir / "refs" / "heads" / "main").write_text("0" * 40 + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="not present in the substrate git object database"):
        PathSubstrateClient(substrate).load_snapshot()
