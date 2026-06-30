from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from lawfirm_os_orchestrator.intake.owner_review import (
    IntakeOwnerReviewError,
    prepare_intake_owner_review_packet,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "intake_owner_review_request.synthetic.json"


def _fixture_payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_intake_owner_review_packet_blocks_until_human_and_decision_model() -> None:
    packet = prepare_intake_owner_review_packet(_fixture_payload())

    assert packet["schema_version"] == "intake_owner_review_packet.v0_1"
    assert packet["status"] == "blocked_pending_owner_review"
    assert packet["non_authoritative"] is True
    assert packet["not_authorized_for_client_submission"] is True
    assert packet["exception_lake_handoff_preview"]["handoff_allowed"] is False
    assert packet["decision_model"]["decision_model_id"] is None
    assert any(
        blocker == "decision_model:missing_promoted_intake_to_budget_decision_model"
        for blocker in packet["blockers"]
    )
    assert any(blocker.startswith("human_pause:") for blocker in packet["blockers"])
    assert any(
        blocker.startswith("budget_precondition:") for blocker in packet["blockers"]
    )


def test_carrier_rejections_classify_known_or_unknown_and_block_unauthorized_appeal() -> (
    None
):
    packet = prepare_intake_owner_review_packet(_fixture_payload())
    report = packet["carrier_rejection_report"]
    notices = {notice["notice_id"]: notice for notice in report["notices"]}

    assert (
        notices["carrier-rejection-001"]["classification_bucket"]
        == "rate_or_cap_rejection"
    )
    assert notices["carrier-rejection-001"]["appeal_requested"] is True
    assert notices["carrier-rejection-001"]["appeal_authorized"] is False
    assert (
        "appeal_authorization_required"
        in notices["carrier-rejection-001"]["response_state_ledger_states"]
    )
    assert (
        "carrier-rejection-001:appeal_requires_human_authorization"
        in report["blockers"]
    )
    assert (
        notices["carrier-rejection-002"]["classification_bucket"]
        == "unknown_or_new_rejection_pattern"
    )
    assert (
        notices["carrier-rejection-002"]["classification_status"]
        == "needs_human_review"
    )
    assert (
        notices["carrier-rejection-002"]["appeal_results_appended"][0]["result"]
        == "partially_granted"
    )
    assert (
        "appeal_result_received"
        in notices["carrier-rejection-002"]["response_state_ledger_states"]
    )


def test_budget_actuals_compare_proposed_compliant_approved_and_actual_by_phase() -> (
    None
):
    packet = prepare_intake_owner_review_packet(_fixture_payload())
    actuals = packet["budget_actuals_variance_report"]

    assert actuals["totals"]["proposed_budget_amount"] == "1200.00"
    assert actuals["totals"]["carrier_compliant_projection_amount"] == "1025.00"
    assert actuals["totals"]["actual_billed_amount"] == "1450.00"
    assert actuals["totals"]["variance_to_proposed"] == "250.00"
    assert (
        actuals["phase_totals"]["initial_case_assessment"][
            "variance_to_approved_if_known"
        ]
        == "300.00"
    )
    line = next(
        line for line in actuals["lines"] if line["line_id"] == "budget-line-l110"
    )
    assert line["variance_to_carrier_compliant_projection"] == "350.00"


def test_intake_owner_review_rejects_real_or_raw_payload_fields() -> None:
    payload = _fixture_payload()
    payload["contains_real_matter_data"] = True

    with pytest.raises(IntakeOwnerReviewError, match="contains_real_matter_data"):
        prepare_intake_owner_review_packet(payload)

    payload = _fixture_payload()
    payload["raw_client_payload"] = {"name": "do not ingest"}
    with pytest.raises(IntakeOwnerReviewError, match="raw_client_payload"):
        prepare_intake_owner_review_packet(payload)


def test_intake_owner_review_rejects_lake_write_modes() -> None:
    payload = _fixture_payload()
    payload["lake_handoff_mode"] = "runtime-safe"

    with pytest.raises(IntakeOwnerReviewError, match="disabled or validate_only"):
        prepare_intake_owner_review_packet(payload)


def test_duplicate_source_hash_blocks_readiness_for_review() -> None:
    payload = _fixture_payload()
    payload["source_refs"][1]["sha256"] = payload["source_refs"][0]["sha256"]

    packet = prepare_intake_owner_review_packet(payload)

    assert packet["source_inventory"]["status"] == "needs_review"
    assert packet["source_inventory"]["duplicate_hashes"] == [
        payload["source_refs"][0]["sha256"]
    ]
    assert "source_inventory_gate" in packet["blockers"]


def test_intake_owner_review_cli_writes_local_artifacts_only(tmp_path: Path) -> None:
    out_dir = tmp_path / "packets"
    ledger_dir = tmp_path / "ledger"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "lawfirm_os_orchestrator",
            "intake",
            "prepare-owner-packet",
            "--input",
            str(FIXTURE),
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
    assert summary["status"] == "blocked_pending_owner_review"
    assert summary["lake_handoff_allowed"] is False
    packet_path = Path(summary["packet_path"])
    assert packet_path.exists()
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    assert packet["exception_lake_handoff_preview"]["lake_write_authority_now"] is False
    assert (packet_path.parent / "exception_lake_handoff_preview.json").exists()
    assert (packet_path.parent / "carrier_rejection_report.json").exists()
    ledger_path = Path(summary["ledger_path"])
    ledger_lines = ledger_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(ledger_lines) == 1
    ledger_record = json.loads(ledger_lines[0])
    assert ledger_record["command_name"] == "intake prepare-owner-packet"
    assert ledger_record["lake_handoff_allowed"] is False
