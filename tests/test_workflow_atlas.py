from __future__ import annotations

import json

from pathlib import Path
from types import SimpleNamespace

from lawfirm_os_orchestrator.commands.workflow_atlas import run
from lawfirm_os_orchestrator.util.json_io import read_json

ROOT = Path(__file__).resolve().parents[1]


def args(tmp_path, lake_mode="disabled"):
    return SimpleNamespace(
        workflow_atlas_command="prepare-meeting",
        topic="Carrier guideline update and pre-bill rework",
        intake=[
            str(ROOT / "examples" / "workflow_atlas" / "billing_specialist_01.synthetic.txt"),
            str(ROOT / "examples" / "workflow_atlas" / "billing_specialist_02.synthetic.txt"),
            str(ROOT / "examples" / "workflow_atlas" / "billing_manager.synthetic.txt"),
        ],
        substrate=str(ROOT / "tests" / "fixtures" / "substrate"),
        ledger_dir=str(tmp_path / "ledger"),
        out_dir=str(tmp_path / "workflow_atlas"),
        lake_mode=lake_mode,
        stdout="json",
    )


def test_prepare_meeting_outputs_candidate_packet(tmp_path):
    code, summary = run(args(tmp_path))
    assert code == 0
    assert summary["status"] == "ok"
    out = Path(summary["output_dir"])
    assert (out / "workflow_fragment.json").exists()
    assert (out / "workflow_diagram.mmd").exists()
    assert (out / "meeting_prep_packet.md").exists()
    fragment = read_json(out / "workflow_fragment.json")
    assert fragment["authority_boundary"]["no_canonical_mutation"] is True
    assert "billblast" in fragment["systems"]


def test_integrity_uses_multiple_same_job_intakes(tmp_path):
    code, summary = run(args(tmp_path))
    assert code == 0
    integrity = read_json(Path(summary["output_dir"]) / "integrity_report.json")
    assert integrity["same_job_role_source_count"] >= 2
    assert integrity["confidence_score"] > 0


def test_priority_links_exception_lake_capture_gap(tmp_path):
    code, summary = run(args(tmp_path, lake_mode="dry-run"))
    assert code == 0
    out = Path(summary["output_dir"])
    priority = read_json(out / "priority_coloring.json")
    lake_signal = read_json(out / "exception_lake_signal.json")
    receipt = read_json(out / "lake_handoff_receipt.json")
    packet_md = (out / "meeting_prep_packet.md").read_text(encoding="utf-8")
    lake_block = packet_md.split("## Exception Lake bridge signal", 1)[1].split("```json", 1)[1].split("```", 1)[0]
    assert priority["lake_evidence_status"] in {"missing_or_partial", "missing_manual", "not_checked"}
    assert lake_signal["canonical_mutation_control"]["direct_mutation_attempted"] is False
    assert json.loads(lake_block)["route_id"] == "route.workflow_escalation.v1"
    assert receipt["mode"] == "dry-run"
    assert receipt["status"] == "accepted"


def test_musk_algorithm_automation_comes_last(tmp_path):
    code, summary = run(args(tmp_path))
    assert code == 0
    musk = read_json(Path(summary["output_dir"]) / "musk_algorithm_review.json")
    assert musk["sequence_rule"] == "question_requirements_delete_simplify_accelerate_automate_last"
    assert musk["requirement_questions"]
    assert musk["automation_candidates_after_simplification"]
