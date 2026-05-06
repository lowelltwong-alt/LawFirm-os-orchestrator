from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from lawfirm_os_orchestrator.evals.shadow import run_shadow_eval
from lawfirm_os_orchestrator.util.json_io import read_json, write_json

ROOT = Path(__file__).resolve().parents[1]


def test_shadow_eval_returns_proposal_only_result(tmp_path):
    result = run_shadow_eval(
        proposal_path=ROOT / "examples" / "shadow_eval" / "validator_threshold_proposal.json",
        fixture_path=ROOT / "evals" / "fixtures" / "classify_exception_cases.jsonl",
        gold_path=ROOT / "evals" / "gold" / "classify_exception_gold.jsonl",
        substrate_root=ROOT / "tests" / "fixtures" / "substrate",
        artifact_root=tmp_path / "artifacts",
        out_path=tmp_path / "shadow.json",
    )

    shadow = result["shadow_eval_result"]
    assert result["semantics"] == "proposal_only"
    assert result["runtime_defaults_changed"] is False
    assert result["writes_to_semantic_substrate"] is False
    assert result["lake_ingest_enabled"] is False
    assert result["boundary_flags"]["may_execute"] is False
    assert shadow["recommended_next_action"] == "request_human_review"
    assert shadow["regression_warnings"] == []
    assert (tmp_path / "shadow.json").exists()


def test_shadow_eval_detects_regression(tmp_path):
    proposal = read_json(ROOT / "examples" / "shadow_eval" / "validator_threshold_proposal.json")
    proposal["proposal_id"] = "proposal_regression_example"
    proposal["candidate_metric_overrides"]["route_exact_match_rate"] = 0.5
    proposal_path = tmp_path / "proposal.json"
    write_json(proposal_path, proposal)

    result = run_shadow_eval(
        proposal_path=proposal_path,
        fixture_path=ROOT / "evals" / "fixtures" / "classify_exception_cases.jsonl",
        gold_path=ROOT / "evals" / "gold" / "classify_exception_gold.jsonl",
        substrate_root=ROOT / "tests" / "fixtures" / "substrate",
        artifact_root=tmp_path / "artifacts",
    )

    shadow = result["shadow_eval_result"]
    assert shadow["recommended_next_action"] == "revise"
    assert any("route_exact_match_rate regressed" in warning for warning in shadow["regression_warnings"])


def test_shadow_eval_fails_closed_on_missing_fixture(tmp_path):
    with pytest.raises(FileNotFoundError, match="fixture"):
        run_shadow_eval(
            proposal_path=ROOT / "examples" / "shadow_eval" / "validator_threshold_proposal.json",
            fixture_path=tmp_path / "missing.jsonl",
            gold_path=ROOT / "evals" / "gold" / "classify_exception_gold.jsonl",
            substrate_root=ROOT / "tests" / "fixtures" / "substrate",
            artifact_root=tmp_path / "artifacts",
        )


def test_run_shadow_eval_script_outputs_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_shadow_eval.py",
            "--proposal",
            "examples/shadow_eval/validator_threshold_proposal.json",
            "--fixture",
            "evals/fixtures/classify_exception_cases.jsonl",
            "--gold",
            "evals/gold/classify_exception_gold.jsonl",
            "--substrate",
            "tests/fixtures/substrate",
            "--artifacts",
            str(tmp_path / "artifacts"),
            "--out",
            str(tmp_path / "shadow.json"),
            "--stdout",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    output = json.loads(completed.stdout)
    assert output["shadow_eval_result"]["recommended_next_action"] == "request_human_review"
    assert output["runtime_defaults_changed"] is False
    assert (tmp_path / "shadow.json").exists()
