from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from lawfirm_os_orchestrator.evals.graders import GoldLabel, grade_case, summarize_grades
from lawfirm_os_orchestrator.evals.runner import run_eval_suite

ROOT = Path(__file__).resolve().parents[1]


def test_eval_suite_computes_required_metrics(tmp_path):
    result = run_eval_suite(
        fixture_path=ROOT / "evals" / "fixtures" / "classify_exception_cases.jsonl",
        gold_path=ROOT / "evals" / "gold" / "classify_exception_gold.jsonl",
        substrate_root=ROOT / "tests" / "fixtures" / "substrate",
        artifact_root=tmp_path / "artifacts",
    )
    metrics = result["metrics"]
    assert metrics["total_cases"] == 3
    assert metrics["route_exact_match_rate"] == 1.0
    assert metrics["event_class_exact_match_rate"] == 1.0
    assert metrics["first_pass_validation_rate"] == 1.0
    assert metrics["evidence_completeness_rate"] == 1.0
    assert metrics["high_confidence_error_count"] == 0
    assert metrics["high_confidence_error_rate"] == 0.0
    assert metrics["average_model_calls_per_run"] == 1.0


def test_eval_suite_model_call_metric_is_stable_across_repeated_runs(tmp_path):
    kwargs = {
        "fixture_path": ROOT / "evals" / "fixtures" / "classify_exception_cases.jsonl",
        "gold_path": ROOT / "evals" / "gold" / "classify_exception_gold.jsonl",
        "substrate_root": ROOT / "tests" / "fixtures" / "substrate",
        "artifact_root": tmp_path / "artifacts",
    }
    first = run_eval_suite(**kwargs)
    second = run_eval_suite(**kwargs)
    assert first["metrics"]["average_model_calls_per_run"] == 1.0
    assert second["metrics"]["average_model_calls_per_run"] == 1.0


def test_unknown_predicted_route_fails_closed_in_grader(tmp_path):
    summary = {
        "status": "ok",
        "route_id": "route.unknown.v1",
        "event_class": "retrieval_miss",
        "confidence": 0.95,
        "evidence_packet_path": str(tmp_path / "missing"),
        "ledger_path": str(tmp_path / "missing.jsonl"),
    }
    grade = grade_case(
        case_id="case",
        summary=summary,
        gold=GoldLabel(case_id="case", route_id="route.retrieval_miss.v1", event_class="retrieval_miss"),
        allowed_route_ids={"route.retrieval_miss.v1"},
        allowed_event_classes={"retrieval_miss"},
    )
    assert grade["route_exact_match"] is False
    assert grade["first_pass_validation"] is False
    assert grade["high_confidence_error"] is True


def test_summarize_rejects_empty_grades():
    with pytest.raises(ValueError, match="zero eval grades"):
        summarize_grades([])


def test_run_evals_script_outputs_json(tmp_path):
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/run_evals.py",
            "--fixture",
            "evals/fixtures/classify_exception_cases.jsonl",
            "--gold",
            "evals/gold/classify_exception_gold.jsonl",
            "--substrate",
            "tests/fixtures/substrate",
            "--artifacts",
            str(tmp_path / "artifacts"),
            "--out",
            str(tmp_path / "metrics.json"),
            "--stdout",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    output = json.loads(completed.stdout)
    assert output["metrics"]["total_cases"] == 3
    assert output["metrics"]["route_exact_match_rate"] == 1.0
    assert (tmp_path / "metrics.json").exists()
