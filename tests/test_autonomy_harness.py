from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
from pydantic import ValidationError

from lawfirm_os_orchestrator.autonomy.autonomy_gate import ActionDescriptor, ActionType, DataScope, RiskColor, classify_autonomy
from lawfirm_os_orchestrator.harness.hardness_scorer import score_hardness
from lawfirm_os_orchestrator.harness.harness_selector import select_harness
from lawfirm_os_orchestrator.harness.leverage_scorer import OpportunityScorecard, score_leverage

ROOT = Path(__file__).resolve().parents[1]


def action(**overrides: object) -> ActionDescriptor:
    payload: dict[str, object] = {
        "action_id": "action_pr02_green_fixture",
        "description": "Create a local synthetic fixture draft.",
        "action_type": "local_artifact_generation",
        "data_scope": "synthetic",
        "local_only": True,
        "reversible": True,
        "inside_preapproved_lane": True,
        "preapproved_lane_id": "LANE-SYNTHETIC-FIXTURE-DRAFTS",
        "source_refs": ["registry/autonomy-lane-registry.json"],
        "audit_evidence_recording_allowed": True,
    }
    payload.update(overrides)
    return ActionDescriptor.model_validate(payload)


def scorecard(**overrides: float | str) -> OpportunityScorecard:
    payload: dict[str, float | str] = {
        "scorecard_id": "scorecard_pr02_fixture",
        "impact": 0.8,
        "recurrence": 0.7,
        "strategic_alignment": 0.9,
        "time_value": 0.6,
        "review_rework_reduction": 0.7,
        "learning_value": 0.8,
        "confidence": 0.9,
        "effort": 0.2,
        "risk": 0.2,
        "dependency": 0.1,
        "governance_load": 0.2,
    }
    payload.update(overrides)
    return OpportunityScorecard.model_validate(payload)


def test_green_classification_requires_preapproved_local_reversible_synthetic_lane():
    decision = classify_autonomy(action())

    assert decision.risk_color == RiskColor.GREEN
    assert decision.human_required is False
    assert decision.human_green_required is False
    assert decision.may_restore_green is False
    assert decision.may_mutate_canon is False


def test_yellow_classification_for_bounded_local_draft_changes():
    decision = classify_autonomy(
        action(
            action_id="action_pr02_yellow_fixture",
            action_type="validator_change",
            inside_preapproved_lane=False,
            preapproved_lane_id=None,
            bounded_change=True,
            needs_review=True,
        )
    )

    assert decision.risk_color == RiskColor.YELLOW
    assert decision.human_required is True
    assert decision.human_green_required is True
    assert "prepare green-candidate recommendation" in decision.allowed_actions


def test_red_classification_for_real_data_and_external_write():
    decision = classify_autonomy(
        action(
            action_id="action_pr02_red_fixture",
            contains_real_client_data=True,
            external_side_effect=True,
        )
    )

    assert decision.risk_color == RiskColor.RED
    assert decision.human_required is True
    assert any("hard red trigger" in reason for reason in decision.reasons)


def test_hard_red_overrides_otherwise_green_conditions():
    decision = classify_autonomy(action(creates_new_route_id=True))

    assert decision.risk_color == RiskColor.RED
    assert "execute final authority" in decision.forbidden_actions


def test_human_green_restoration_attempt_is_red_and_human_required():
    decision = classify_autonomy(action(attempts_green_restoration=True))

    assert decision.risk_color == RiskColor.RED
    assert decision.human_green_required is True
    assert decision.may_restore_green is False


@pytest.mark.parametrize(
    ("action_type", "reversible", "local_only", "expected_level"),
    [
        ("deterministic_check", True, True, 0),
        ("local_artifact_generation", True, True, 1),
        ("doc_change", True, True, 2),
        ("validator_change", True, True, 3),
        ("autonomy_change", True, True, 4),
        ("unknown", True, True, 5),
        ("doc_change", False, True, 4),
        ("doc_change", True, False, 5),
    ],
)
def test_hardness_maps_to_h0_h5(action_type: str, reversible: bool, local_only: bool, expected_level: int):
    hardness = score_hardness(action(action_type=action_type, reversible=reversible, local_only=local_only))

    assert hardness.hardness_level == expected_level
    assert hardness.hardness_band == f"H{expected_level}"
    assert hardness.controls_harness_depth_only is True


def test_leverage_scoring_is_deterministic_bounded_and_priority_only():
    first = score_leverage(scorecard())
    second = score_leverage(scorecard())

    assert first.leverage_score == second.leverage_score
    assert 0.0 <= first.leverage_score <= 1.0
    assert first.priority_band == "high"
    assert first.controls_priority_only is True


def test_invalid_leverage_inputs_fail_validation():
    with pytest.raises(ValidationError):
        scorecard(impact=1.5)


def test_no_hardness_or_leverage_authority_upgrade_for_yellow():
    decision = classify_autonomy(
        action(
            action_id="action_pr02_yellow_hard_fixture",
            action_type="autonomy_change",
            inside_preapproved_lane=False,
            preapproved_lane_id=None,
            bounded_change=True,
            needs_review=True,
        )
    )
    plan = select_harness(autonomy=decision, hardness=score_hardness(action(action_type="autonomy_change")), leverage=score_leverage(scorecard()))

    assert decision.risk_color == RiskColor.YELLOW
    assert plan.risk_color == RiskColor.YELLOW
    assert plan.harness_level == "H4"
    assert plan.human_required is True
    assert "green restoration" in plan.forbidden_outputs


def test_red_always_selects_human_required_h5_harness():
    decision = classify_autonomy(action(canon_mutation=True))
    plan = select_harness(autonomy=decision, hardness=score_hardness(action(action_type="deterministic_check")), leverage=score_leverage(scorecard()))

    assert plan.risk_color == RiskColor.RED
    assert plan.harness_level == "H5"
    assert plan.human_required is True
    assert "human_decision_owner" in plan.required_agents


def test_green_hard_work_gets_stronger_harness_but_not_higher_authority():
    hard_green = action(action_type="code_change")
    decision = classify_autonomy(hard_green)
    plan = select_harness(autonomy=decision, hardness=score_hardness(hard_green), leverage=score_leverage(scorecard()))

    assert decision.risk_color == RiskColor.GREEN
    assert plan.risk_color == RiskColor.GREEN
    assert plan.harness_level in {"H3", "H4", "H5"}
    assert plan.human_required is False
    assert "Semantic Substrate mutation" in plan.forbidden_outputs


def test_cli_classify_autonomy_and_select_harness_output_inert_json():
    artifact_dir = ROOT / ".lawfirm-os-orchestrator" / "test-artifacts" / f"pr02-{uuid.uuid4().hex}"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    action_path = artifact_dir / "action.json"
    autonomy_out = artifact_dir / "autonomy.json"
    scorecard_path = artifact_dir / "scorecard.json"
    harness_out = artifact_dir / "harness.json"
    action_path.write_text(json.dumps(action().model_dump(mode="json")), encoding="utf-8")
    scorecard_path.write_text(json.dumps(scorecard().model_dump(mode="json")), encoding="utf-8")

    autonomy_completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "lawfirm_os_orchestrator",
            "classify-autonomy",
            "--action",
            str(action_path),
            "--out",
            str(autonomy_out),
            "--stdout",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    autonomy_output = json.loads(autonomy_completed.stdout)
    assert autonomy_output["status"] == "ok"
    assert autonomy_output["runs_git"] is False
    assert autonomy_output["writes_to_semantic_substrate"] is False
    assert autonomy_out.exists()

    harness_completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "lawfirm_os_orchestrator",
            "select-harness",
            "--autonomy",
            str(autonomy_out),
            "--scorecard",
            str(scorecard_path),
            "--out",
            str(harness_out),
            "--stdout",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    harness_output = json.loads(harness_completed.stdout)
    assert harness_output["status"] == "ok"
    assert harness_output["calls_model"] is False
    assert harness_output["calls_network"] is False
    assert harness_output["harness_plan"]["forbidden_outputs"]
    assert harness_out.exists()
