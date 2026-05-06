from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, "-m", "lawfirm_os_orchestrator", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def assert_inert(output: dict[str, object]) -> None:
    assert output["status"] == "ok"
    assert output["local_artifact_only"] is True
    assert output["runs_git"] is False
    assert output["applies_patch"] is False
    assert output["writes_to_semantic_substrate"] is False
    assert output["lake_writes"] is False


def test_learning_run_shadow_eval_cli_outputs_inert_json(tmp_path):
    output = run_cli(
        "learning",
        "run-shadow-eval",
        "--proposal",
        "examples/shadow_eval/validator_threshold_proposal.json",
        "--artifacts",
        str(tmp_path / "artifacts"),
        "--out",
        str(tmp_path / "shadow.json"),
        "--stdout",
        "json",
    )

    assert_inert(output)
    assert output["proposal_id"] == "proposal_validator_threshold_example"
    assert Path(output["shadow_eval_result"]["shadow_eval_result_id"])
    assert (tmp_path / "shadow.json").exists()


def test_learning_build_upgrade_proposal_cli_outputs_inert_json(tmp_path):
    output = run_cli(
        "learning",
        "build-upgrade-proposal",
        "--input",
        "examples/upgrade_proposals/validator_threshold_packet_request.json",
        "--out",
        str(tmp_path / "packets"),
        "--stdout",
        "json",
    )

    assert_inert(output)
    assert output["proposal_id"] == "upgrade_proposal_validator_threshold_example"
    assert Path(output["files"]["proposal"]).exists()


def test_learning_render_codex_task_cli_outputs_inert_json(tmp_path):
    output = run_cli(
        "learning",
        "render-codex-task",
        "--input",
        "examples/codex_task_drafts/validator_task_draft_request.json",
        "--out",
        str(tmp_path / "draft"),
        "--stdout",
        "json",
    )

    assert_inert(output)
    assert output["runs_codex"] is False
    assert Path(output["files"]["codex_task_draft_markdown"]).exists()


def test_learning_score_insight_cli_outputs_inert_json(tmp_path):
    out = tmp_path / "score.json"
    output = run_cli(
        "learning",
        "score-insight",
        "--input",
        "examples/research_signals/algorithm_insight_example.json",
        "--out",
        str(out),
        "--stdout",
        "json",
    )

    assert_inert(output)
    assert output["semantics"] == "proposal_only"
    assert output["target_surface"] == "validators"
    assert output["upgrade_priority"] > 0
    assert out.exists()
