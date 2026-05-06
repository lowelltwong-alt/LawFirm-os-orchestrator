from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from lawfirm_os_orchestrator.learning.proposals import (
    UpgradeProposalPacketRequest,
    build_upgrade_proposal_packet,
)
from lawfirm_os_orchestrator.util.json_io import read_json

ROOT = Path(__file__).resolve().parents[1]


def test_upgrade_proposal_packet_writes_required_local_artifacts(tmp_path):
    result = build_upgrade_proposal_packet(
        request_path=ROOT / "examples" / "upgrade_proposals" / "validator_threshold_packet_request.json",
        output_root=tmp_path / "packets",
    )
    packet_dir = Path(str(result["packet_dir"]))
    expected = {
        "proposal.json",
        "evidence_refs.json",
        "experiment_plan.json",
        "shadow_eval_result.json",
        "risk_review.md",
        "codex_task_draft.md",
    }

    assert {path.name for path in packet_dir.iterdir()} == expected
    proposal = read_json(packet_dir / "proposal.json")
    assert proposal["proposal"]["implementation_allowed"] is False
    assert proposal["automatic_implementation"] is False
    assert proposal["git_operations"] is False
    assert proposal["semantic_substrate_writes"] is False
    assert proposal["lake_writes"] is False
    assert proposal["boundary_flags"]["may_mutate_canon"] is False


def test_upgrade_proposal_packet_rejects_forbidden_target_surface():
    raw = read_json(ROOT / "examples" / "upgrade_proposals" / "validator_threshold_packet_request.json")
    raw["target_surface"] = "canonical_route_ids"
    with pytest.raises(ValidationError):
        UpgradeProposalPacketRequest.model_validate(raw)


def test_upgrade_proposal_packet_markdown_is_review_only(tmp_path):
    result = build_upgrade_proposal_packet(
        request_path=ROOT / "examples" / "upgrade_proposals" / "validator_threshold_packet_request.json",
        output_root=tmp_path / "packets",
    )
    packet_dir = Path(str(result["packet_dir"]))
    risk_review = (packet_dir / "risk_review.md").read_text(encoding="utf-8")
    task_draft = (packet_dir / "codex_task_draft.md").read_text(encoding="utf-8")

    assert "proposal-only local artifact" in risk_review
    assert "no code mutation" in risk_review
    assert "no Git operations" in risk_review
    assert "not invoked by the Orchestrator" in task_draft


def test_build_upgrade_proposal_script_outputs_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/build_upgrade_proposal.py",
            "--input",
            "examples/upgrade_proposals/validator_threshold_packet_request.json",
            "--out",
            str(tmp_path / "packets"),
            "--stdout",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    output = json.loads(completed.stdout)
    assert output["proposal_id"] == "upgrade_proposal_validator_threshold_example"
    assert output["automatic_implementation"] is False
    assert Path(output["files"]["proposal"]).exists()
