from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.autonomy.autonomy_gate import ActionDescriptor, AutonomyDecision, classify_autonomy
from lawfirm_os_orchestrator.autonomy.green_lane_watcher import watch_green_lanes
from lawfirm_os_orchestrator.harness.hardness_scorer import HardnessScore, score_hardness
from lawfirm_os_orchestrator.harness.harness_selector import select_harness
from lawfirm_os_orchestrator.harness.leverage_scorer import OpportunityScorecard, score_leverage
from lawfirm_os_orchestrator.util.json_io import read_json, write_json

EXIT_AUTONOMY_HARNESS = 2


def _with_status(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "local_artifact_only": True,
        "runs_git": False,
        "applies_patch": False,
        "writes_to_semantic_substrate": False,
        "lake_writes": False,
        "calls_model": False,
        "calls_network": False,
        "external_writes": False,
        **payload,
    }


def run_classify_autonomy(args) -> tuple[int, dict[str, Any]]:
    try:
        action = ActionDescriptor.model_validate(read_json(Path(args.action)))
        decision = classify_autonomy(action)
        hardness = score_hardness(action)
        result = {
            "action": action.model_dump(mode="json"),
            "autonomy_decision": decision.model_dump(mode="json"),
            "hardness_score": hardness.model_dump(mode="json"),
        }
        write_json(Path(args.out), result)
        return 0, _with_status(result)
    except Exception as exc:
        return EXIT_AUTONOMY_HARNESS, {"status": "failed_validation", "error": str(exc)}


def run_select_harness(args) -> tuple[int, dict[str, Any]]:
    try:
        autonomy_payload = read_json(Path(args.autonomy))
        decision_payload = autonomy_payload.get("autonomy_decision", autonomy_payload)
        action_payload = autonomy_payload.get("action")
        hardness_payload = autonomy_payload.get("hardness_score")
        decision = classify_autonomy(ActionDescriptor.model_validate(action_payload)) if action_payload else None
        autonomy_decision = decision or AutonomyDecision.model_validate(decision_payload)
        hardness = (
            score_hardness(ActionDescriptor.model_validate(action_payload))
            if action_payload
            else HardnessScore.model_validate(hardness_payload)
        )
        scorecard = OpportunityScorecard.model_validate(read_json(Path(args.scorecard)))
        leverage = score_leverage(scorecard)
        harness = select_harness(autonomy=autonomy_decision, hardness=hardness, leverage=leverage)
        result = {
            "autonomy_decision": autonomy_decision.model_dump(mode="json"),
            "hardness_score": hardness.model_dump(mode="json"),
            "leverage_score": leverage.model_dump(mode="json"),
            "harness_plan": harness.model_dump(mode="json"),
        }
        write_json(Path(args.out), result)
        return 0, _with_status(result)
    except Exception as exc:
        return EXIT_AUTONOMY_HARNESS, {"status": "failed_validation", "error": str(exc)}


def run_watch_green_lanes(args) -> tuple[int, dict[str, Any]]:
    try:
        return 0, watch_green_lanes(signals_path=Path(args.signals), lanes_path=Path(args.lanes), out_path=Path(args.out))
    except Exception as exc:
        return EXIT_AUTONOMY_HARNESS, {"status": "failed_validation", "error": str(exc)}
