from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from lawfirm_os_orchestrator.evals.runner import run_eval_suite
from lawfirm_os_orchestrator.learning.models import ExperimentPlan, ShadowEvalResult, TargetSurface, boundary_flags
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.json_io import read_json, write_json

LOWER_IS_BETTER_METRICS = {
    "high_confidence_error_count",
    "high_confidence_error_rate",
    "average_model_calls_per_run",
}


class ShadowEvalProposal(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    proposal_id: str = Field(min_length=1)
    hypothesis_id: str = Field(default_factory=lambda: new_id("upgrade_hypothesis"), min_length=1)
    experiment_plan_id: str = Field(default_factory=lambda: new_id("experiment_plan"), min_length=1)
    target_surface: TargetSurface
    affected_metric: str = Field(min_length=1)
    candidate_change_summary: str = Field(min_length=1)
    eval_suite_ref: str = Field(min_length=1)
    baseline_ref: str = Field(min_length=1)
    success_metrics: list[str] = Field(min_length=1)
    failure_thresholds: dict[str, float] = Field(default_factory=dict)
    candidate_metric_overrides: dict[str, float] = Field(default_factory=dict)
    notes: str | None = None


def load_shadow_eval_proposal(path: Path) -> ShadowEvalProposal:
    if not path.exists():
        raise FileNotFoundError(f"Shadow eval proposal not found: {path}")
    return ShadowEvalProposal.model_validate(read_json(path))


def _numeric_metrics(metrics: dict[str, Any]) -> dict[str, float]:
    numeric: dict[str, float] = {}
    for key, value in metrics.items():
        if isinstance(value, bool):
            continue
        if isinstance(value, int | float):
            numeric[key] = float(value)
    return numeric


def _metric_deltas(baseline: dict[str, float], candidate: dict[str, float]) -> dict[str, float]:
    return {
        metric: round(candidate[metric] - baseline[metric], 10)
        for metric in sorted(set(baseline) & set(candidate))
    }


def _regression_warnings(
    *,
    baseline: dict[str, float],
    candidate: dict[str, float],
    thresholds: dict[str, float],
) -> list[str]:
    warnings: list[str] = []
    for metric in sorted(set(baseline) & set(candidate)):
        tolerance = max(0.0, float(thresholds.get(metric, 0.0)))
        delta = candidate[metric] - baseline[metric]
        if metric in LOWER_IS_BETTER_METRICS:
            if delta > tolerance:
                warnings.append(f"{metric} regressed by {delta:.6f}")
        elif delta < -tolerance:
            warnings.append(f"{metric} regressed by {abs(delta):.6f}")
    return warnings


def run_shadow_eval(
    *,
    proposal_path: Path,
    fixture_path: Path,
    gold_path: Path,
    substrate_root: Path,
    artifact_root: Path,
    out_path: Path | None = None,
) -> dict[str, Any]:
    if not fixture_path.exists():
        raise FileNotFoundError(f"Eval fixture not found: {fixture_path}")
    if not gold_path.exists():
        raise FileNotFoundError(f"Eval gold labels not found: {gold_path}")

    proposal = load_shadow_eval_proposal(proposal_path)
    baseline_result = run_eval_suite(
        fixture_path=fixture_path,
        gold_path=gold_path,
        substrate_root=substrate_root,
        artifact_root=artifact_root,
    )
    baseline_metrics = _numeric_metrics(baseline_result["metrics"])
    candidate_metrics = dict(baseline_metrics)
    candidate_metrics.update(proposal.candidate_metric_overrides)
    deltas = _metric_deltas(baseline_metrics, candidate_metrics)
    warnings = _regression_warnings(
        baseline=baseline_metrics,
        candidate=candidate_metrics,
        thresholds=proposal.failure_thresholds,
    )
    next_action: Literal["revise", "request_human_review"] = "revise" if warnings else "request_human_review"

    experiment_plan = ExperimentPlan(
        experiment_plan_id=proposal.experiment_plan_id,
        hypothesis_id=proposal.hypothesis_id,
        eval_suite_ref=proposal.eval_suite_ref,
        baseline_ref=proposal.baseline_ref,
        candidate_change_summary=proposal.candidate_change_summary,
        success_metrics=proposal.success_metrics,
        failure_thresholds=proposal.failure_thresholds,
    )
    shadow_result = ShadowEvalResult(
        experiment_plan_id=experiment_plan.experiment_plan_id,
        baseline_metrics=baseline_metrics,
        candidate_metrics=candidate_metrics,
        metric_deltas=deltas,
        regression_warnings=warnings,
        recommended_next_action=next_action,
    )
    result = {
        "schema_version": "1.0",
        "semantics": "proposal_only",
        "proposal_id": proposal.proposal_id,
        "target_surface": proposal.target_surface.value,
        "affected_metric": proposal.affected_metric,
        "baseline_eval": baseline_result,
        "experiment_plan": experiment_plan.model_dump(mode="json"),
        "shadow_eval_result": shadow_result.model_dump(mode="json"),
        "boundary_flags": boundary_flags(shadow_result),
        "runtime_defaults_changed": False,
        "writes_to_semantic_substrate": False,
        "lake_ingest_enabled": False,
    }
    if out_path is not None:
        write_json(out_path, result)
    return result
