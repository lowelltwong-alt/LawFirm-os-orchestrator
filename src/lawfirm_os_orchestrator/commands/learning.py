from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.evals.shadow import run_shadow_eval
from lawfirm_os_orchestrator.learning.codex_tasks import write_codex_task_artifacts
from lawfirm_os_orchestrator.learning.models import AlgorithmInsight
from lawfirm_os_orchestrator.learning.proposals import build_upgrade_proposal_packet
from lawfirm_os_orchestrator.learning.scoring import score_algorithm_insight
from lawfirm_os_orchestrator.util.json_io import read_json, write_json

EXIT_LEARNING = 2


def _with_status(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "ok",
        "proposal_only": payload.get("semantics") == "proposal_only",
        "local_artifact_only": bool(payload.get("local_artifact_only", True)),
        "runs_git": bool(payload.get("runs_git", False)),
        "applies_patch": bool(payload.get("applies_patch", False)),
        "writes_to_semantic_substrate": bool(payload.get("writes_to_semantic_substrate", False)),
        "lake_writes": bool(payload.get("lake_writes", False)),
        **payload,
    }


def run(args) -> tuple[int, dict[str, Any]]:
    try:
        if args.learning_command == "run-shadow-eval":
            result = run_shadow_eval(
                proposal_path=Path(args.proposal),
                fixture_path=Path(args.fixture),
                gold_path=Path(args.gold),
                substrate_root=Path(args.substrate),
                artifact_root=Path(args.artifacts),
                out_path=Path(args.out),
            )
            return 0, _with_status(result)
        if args.learning_command == "build-upgrade-proposal":
            result = build_upgrade_proposal_packet(request_path=Path(args.input), output_root=Path(args.out))
            return 0, _with_status(result)
        if args.learning_command == "render-codex-task":
            result = write_codex_task_artifacts(request_path=Path(args.input), output_dir=Path(args.out))
            return 0, _with_status(result)
        if args.learning_command == "score-insight":
            insight = AlgorithmInsight.model_validate(read_json(Path(args.input)))
            result = score_algorithm_insight(insight)
            if args.out:
                write_json(Path(args.out), result)
            return 0, _with_status(
                {
                    **result,
                    "local_artifact_only": True,
                    "runs_git": False,
                    "applies_patch": False,
                    "writes_to_semantic_substrate": False,
                    "lake_writes": False,
                }
            )
    except Exception as exc:
        return EXIT_LEARNING, {"status": "failed_validation", "error": str(exc)}
    return EXIT_LEARNING, {"status": "failed_validation", "error": f"unknown learning command: {args.learning_command}"}
