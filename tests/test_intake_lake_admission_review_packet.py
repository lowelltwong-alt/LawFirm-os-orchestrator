from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from lawfirm_os_orchestrator.intake.lake_admission_review import (
    IntakeLakeAdmissionReviewError,
    prepare_intake_lake_admission_review_packet,
)
from lawfirm_os_orchestrator.intake.owner_review import (
    prepare_intake_owner_review_packet,
)
from lawfirm_os_orchestrator.util.hashing import canonical_json


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "intake_owner_review_request.synthetic.json"


def _fixture_payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _owner_packet() -> dict:
    return prepare_intake_owner_review_packet(_fixture_payload())


def _rehash_owner_packet(packet: dict) -> dict:
    clean = {key: value for key, value in packet.items() if key != "packet_hash"}
    packet["packet_hash"] = hashlib.sha256(canonical_json(clean)).hexdigest()
    return packet


def test_lake_admission_review_packet_blocks_and_summarizes_candidate_families() -> (
    None
):
    owner_packet = _owner_packet()

    packet = prepare_intake_lake_admission_review_packet(owner_packet)

    assert packet["schema_version"] == "intake_lake_admission_review_packet.v0_1"
    assert packet["status"] == "blocked_pending_exception_lake_owner_review"
    assert packet["owner_packet_hash"] == owner_packet["packet_hash"]
    assert packet["non_authoritative"] is True
    assert packet["not_authorized_for_client_submission"] is True
    controls = packet["admission_controls"]
    assert controls["lake_write_authority_now"] is False
    assert controls["lake_handoff_allowed"] is False
    assert controls["sqlite_write_authorized_now"] is False
    assert controls["raw_payload_storage_allowed"] is False
    assert controls["canonical_route_id_assignment"] == "none"
    assert controls["canonical_event_class_assignment"] == "none"
    families = set(packet["candidate_admission_record_families"])
    assert "intake_proposal_packet" in families
    assert "intake_escalation_or_blocker" in families
    assert "budget_actual_comparison" in families
    assert "budget_actual_variance_driver_candidate" in families
    assert "carrier_rejection_notice" in families
    assert "carrier_rejection_reconciliation" in families
    assert "carrier_appeal_result" in families
    assert "carrier_financial_outcome" in families
    assert "carrier_rejection_learning_candidate" in families
    assert "exception_lake_owner_contract:required" in packet["blockers"]
    assert all(
        record["admission_status"] == "not_admitted"
        for record in packet["candidate_record_summaries"]
    )
    assert all(
        record["record_hash_required_before_admission"] is True
        for record in packet["candidate_record_summaries"]
    )


def test_lake_admission_review_rejects_tampered_owner_packet_hash() -> None:
    owner_packet = _owner_packet()
    owner_packet["blockers"].append("tamper")

    with pytest.raises(IntakeLakeAdmissionReviewError, match="packet_hash"):
        prepare_intake_lake_admission_review_packet(owner_packet)


def test_lake_admission_review_rejects_lake_write_authority_claim() -> None:
    owner_packet = _owner_packet()
    owner_packet["exception_lake_handoff_preview"]["lake_write_authority_now"] = True
    _rehash_owner_packet(owner_packet)

    with pytest.raises(IntakeLakeAdmissionReviewError, match="Lake write authority"):
        prepare_intake_lake_admission_review_packet(owner_packet)


def test_lake_admission_review_rejects_raw_or_real_owner_packet_fields() -> None:
    owner_packet = _owner_packet()
    owner_packet["raw_client_payload"] = {"name": "forbidden"}
    _rehash_owner_packet(owner_packet)

    with pytest.raises(IntakeLakeAdmissionReviewError, match="raw_client_payload"):
        prepare_intake_lake_admission_review_packet(owner_packet)


def test_lake_admission_review_cli_writes_local_artifacts_only(tmp_path: Path) -> None:
    owner_packet_path = tmp_path / "owner_packet.json"
    owner_packet_path.write_text(json.dumps(_owner_packet()), encoding="utf-8")
    out_dir = tmp_path / "packets"
    ledger_dir = tmp_path / "ledger"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "lawfirm_os_orchestrator",
            "intake",
            "build-lake-admission-review-packet",
            "--owner-packet",
            str(owner_packet_path),
            "--out-dir",
            str(out_dir),
            "--ledger-dir",
            str(ledger_dir),
            "--stdout",
            "json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    summary = json.loads(completed.stdout)
    assert summary["status"] == "blocked_pending_exception_lake_owner_review"
    assert summary["lake_handoff_allowed"] is False
    assert summary["sqlite_write_authorized_now"] is False
    packet_path = Path(summary["packet_path"])
    assert packet_path.exists()
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    assert packet["admission_controls"]["lake_write_authority_now"] is False
    assert packet["admission_controls"]["sqlite_write_authorized_now"] is False
    assert (packet_path.parent / "candidate_record_summaries.json").exists()
    assert Path(summary["markdown_path"]).exists()
    ledger_path = Path(summary["ledger_path"])
    ledger_lines = ledger_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(ledger_lines) == 1
    ledger_record = json.loads(ledger_lines[0])
    assert ledger_record["command_name"] == "intake build-lake-admission-review-packet"
    assert ledger_record["lake_handoff_allowed"] is False
    assert ledger_record["sqlite_write_authorized_now"] is False
