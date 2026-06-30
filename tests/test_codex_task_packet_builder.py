from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path

from lawfirm_os_orchestrator.autonomy.autonomy_gate import (
    ActionDescriptor,
    RiskColor,
    classify_autonomy,
)
from lawfirm_os_orchestrator.harness.agent_committee import build_agent_review_plan
from lawfirm_os_orchestrator.harness.codex_task_builder import (
    OpportunityInput,
    build_codex_task_packet,
)
from lawfirm_os_orchestrator.harness.hardness_scorer import score_hardness
from lawfirm_os_orchestrator.harness.harness_selector import select_harness
from lawfirm_os_orchestrator.harness.leverage_scorer import (
    OpportunityScorecard,
    score_leverage,
)

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PACKET_FIELDS = {
    "schema_version",
    "task_packet_id",
    "generated_at",
    "objective",
    "source_refs",
    "repos_touched",
    "risk_color",
    "harness_level",
    "leverage_score",
    "hardness_level",
    "autonomy_decision_ref",
    "harness_plan_ref",
    "allowed_actions",
    "forbidden_actions",
    "files_to_add_or_update",
    "acceptance_criteria",
    "tests_to_run",
    "rollback_rule",
    "docs_updates_required",
    "safety_invariants",
    "human_approval_requirements",
    "expected_output_artifacts",
    "implementation_notes",
    "stop_conditions",
}


def artifact_dir() -> Path:
    path = (
        ROOT
        / ".lawfirm-os-orchestrator"
        / "test-artifacts"
        / f"pr04-{uuid.uuid4().hex}"
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


def action(**overrides: object) -> ActionDescriptor:
    payload: dict[str, object] = {
        "action_id": "action_pr04_fixture",
        "description": "Build inert local task packet.",
        "action_type": "codex_task_packet_draft",
        "data_scope": "metadata_only",
        "local_only": True,
        "reversible": True,
        "inside_preapproved_lane": True,
        "preapproved_lane_id": "LANE-CODEX-TASK-PACKET-DRAFTS",
        "source_refs": ["registry/autonomy-lane-registry.json"],
        "audit_evidence_recording_allowed": True,
    }
    payload.update(overrides)
    return ActionDescriptor.model_validate(payload)


def scorecard(**overrides: float | str) -> OpportunityScorecard:
    payload: dict[str, float | str] = {
        "scorecard_id": "scorecard_pr04_fixture",
        "impact": 0.7,
        "recurrence": 0.7,
        "strategic_alignment": 0.8,
        "time_value": 0.6,
        "review_rework_reduction": 0.8,
        "learning_value": 0.8,
        "confidence": 0.9,
        "effort": 0.2,
        "risk": 0.2,
        "dependency": 0.1,
        "governance_load": 0.2,
    }
    payload.update(overrides)
    return OpportunityScorecard.model_validate(payload)


def opportunity() -> OpportunityInput:
    return OpportunityInput.model_validate(
        {
            "opportunity_id": "OPP-PR04-001",
            "objective": "Generate an inert Codex task packet for local review.",
            "source_refs": ["local://opportunity/pr04"],
            "repos_touched": ["LawFirm-os-orchestrator"],
            "files_to_add_or_update": [
                "src/lawfirm_os_orchestrator/harness/codex_task_builder.py"
            ],
            "acceptance_criteria": [
                "packet is inert",
                "packet preserves risk authority",
            ],
            "tests_to_run": [
                "python scripts/run_full_pytest.py",
                "python scripts/check_safety.py --stdout json",
            ],
            "docs_updates_required": ["README.md", "DATA_FLOW_MAP.md"],
            "expected_output_artifacts": ["codex_task_packet.json"],
            "implementation_notes": ["Do not execute this packet automatically."],
            "stop_conditions": ["stop if task requires external writes"],
        }
    )


def packet_for(action_payload: ActionDescriptor):
    decision = classify_autonomy(action_payload)
    hardness = score_hardness(action_payload)
    leverage = score_leverage(scorecard())
    harness = select_harness(autonomy=decision, hardness=hardness, leverage=leverage)
    return build_codex_task_packet(
        opportunity=opportunity(),
        scorecard=scorecard(),
        autonomy=decision,
        harness=harness,
    )


def test_task_packet_contains_all_required_fields_and_requirements():
    packet = packet_for(action())
    payload = packet.model_dump(mode="json")

    assert REQUIRED_PACKET_FIELDS <= set(payload)
    assert payload["docs_updates_required"]
    assert payload["tests_to_run"]
    assert "python scripts/run_full_pytest.py" in payload["tests_to_run"]
    assert payload["rollback_rule"]
    assert payload["acceptance_criteria"]


def test_yellow_packet_preserves_authority_limits():
    packet = packet_for(
        action(
            action_type="validator_change",
            inside_preapproved_lane=False,
            preapproved_lane_id=None,
            bounded_change=True,
            needs_review=True,
        )
    )

    assert packet.risk_color == RiskColor.YELLOW
    assert "auto-merge" in packet.forbidden_actions
    assert "production release" in packet.forbidden_actions
    assert "canon mutation" in packet.forbidden_actions
    assert (
        "human review required before final authority"
        in packet.human_approval_requirements
    )


def test_red_packet_is_human_required_and_decision_packet_only():
    packet = packet_for(action(contains_real_client_data=True))

    assert packet.risk_color == RiskColor.RED
    assert packet.allowed_actions == [
        "prepare proposal-only risk memo",
        "prepare human decision packet",
    ]
    assert (
        "human approval required before any execution authority"
        in packet.human_approval_requirements
    )
    assert "external writes" in packet.forbidden_actions
    assert "live model calls" in packet.forbidden_actions


def test_green_packet_does_not_allow_canon_mutation_external_writes_or_green_restoration():
    packet = packet_for(action())

    assert packet.risk_color == RiskColor.GREEN
    assert "canon mutation" in packet.forbidden_actions
    assert "external writes" in packet.forbidden_actions
    assert "green restoration by agents" in packet.forbidden_actions


def test_task_packet_builder_is_inert():
    packet = packet_for(action())

    assert packet.runs_codex is False
    assert packet.runs_git is False
    assert packet.creates_branch is False
    assert packet.pushes_git is False
    assert packet.applies_patch is False
    assert packet.runs_tests is False
    assert packet.calls_model is False
    assert packet.calls_network is False
    assert packet.writes_to_semantic_substrate is False
    assert packet.lake_writes is False


def test_agent_committee_builder_is_inert():
    review = build_agent_review_plan(
        risk_color=RiskColor.RED, harness_level="H5", source_refs=["local://review"]
    )

    assert review.human_decision_required is True
    assert review.inert_review_plan_only is True
    assert review.may_call_model is False
    assert review.may_call_network is False
    assert review.may_run_git is False
    assert "execute Git" in review.forbidden_review_outputs


def test_cli_generate_codex_task_writes_local_artifact():
    root = artifact_dir()
    action_payload = action()
    decision = classify_autonomy(action_payload)
    hardness = score_hardness(action_payload)
    harness = select_harness(
        autonomy=decision, hardness=hardness, leverage=score_leverage(scorecard())
    )
    opportunity_path = root / "opportunity.json"
    scorecard_path = root / "scorecard.json"
    autonomy_path = root / "autonomy.json"
    harness_path = root / "harness.json"
    out_path = root / "codex_task_packet.json"
    opportunity_path.write_text(
        json.dumps(opportunity().model_dump(mode="json")), encoding="utf-8"
    )
    scorecard_path.write_text(
        json.dumps(scorecard().model_dump(mode="json")), encoding="utf-8"
    )
    autonomy_path.write_text(
        json.dumps({"autonomy_decision": decision.model_dump(mode="json")}),
        encoding="utf-8",
    )
    harness_path.write_text(
        json.dumps({"harness_plan": harness.model_dump(mode="json")}), encoding="utf-8"
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "lawfirm_os_orchestrator",
            "generate-codex-task",
            "--opportunity",
            str(opportunity_path),
            "--scorecard",
            str(scorecard_path),
            "--autonomy",
            str(autonomy_path),
            "--harness",
            str(harness_path),
            "--out",
            str(out_path),
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
    assert output["runs_codex"] is False
    assert output["runs_git"] is False
    assert output["calls_model"] is False
    assert output["calls_network"] is False
    assert output["writes_to_semantic_substrate"] is False
    assert output["lake_writes"] is False
    assert output["task_packet"]["objective"] == opportunity().objective
    assert out_path.exists()


def test_no_git_network_model_execution_paths_exist():
    source_paths = [
        ROOT / "src" / "lawfirm_os_orchestrator" / "harness" / "codex_task_builder.py",
        ROOT / "src" / "lawfirm_os_orchestrator" / "harness" / "agent_committee.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in source_paths)

    assert "subprocess" not in combined
    assert "socket" not in combined
    assert "requests" not in combined
    assert "httpx" not in combined
    assert "urllib" not in combined
    assert "openai" not in combined
    assert "git commit" not in combined
    assert "git push" not in combined
