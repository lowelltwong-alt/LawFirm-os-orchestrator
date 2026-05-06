from __future__ import annotations

import pytest
from pydantic import ValidationError

from lawfirm_os_orchestrator.learning.models import (
    ActionRecommendation,
    AlgorithmInsight,
    CodexTaskDraft,
    DefectCategory,
    DefectTag,
    ExperimentPlan,
    LEARNING_MODEL_TYPES,
    LearningCandidate,
    PressureVector,
    ReviewerCorrection,
    ShadowEvalResult,
    TargetSurface,
    UpgradeHypothesis,
    UpgradeProposal,
    boundary_flags,
)


def sample_defect_tag() -> DefectTag:
    return DefectTag(
        category=DefectCategory.STRUCTURAL,
        target_surface=TargetSurface.VALIDATORS,
        severity="medium",
        description="Synthetic validator defect candidate.",
        evidence_refs=["synthetic://evidence/001"],
    )


def sample_models():
    defect = sample_defect_tag()
    correction = ReviewerCorrection(
        run_id="run_001",
        reviewer_ref="reviewer://synthetic",
        original_route_id="route.workflow_escalation.v1",
        corrected_route_id="route.workflow_escalation.v1",
        original_event_class="workflow_escalation",
        corrected_event_class="workflow_escalation",
        defect_tags=[defect],
        rationale="Synthetic reviewer correction for model testing.",
    )
    pressure = PressureVector(
        target_surface=TargetSurface.VALIDATORS,
        defect_tags=[defect],
        recurrence_count=2,
        impact=0.4,
        detectability=0.8,
        candidate_causes=["validator threshold too permissive"],
        smallest_plausible_intervention="Add a stricter fixture-backed validator check.",
    )
    candidate = LearningCandidate(
        candidate_type="pressure_vector",
        source_refs=[pressure.pressure_vector_id],
        target_surface=TargetSurface.VALIDATORS,
        summary="Synthetic pressure vector candidate.",
        pressure_vector_id=pressure.pressure_vector_id,
        defect_tag_ids=[defect.defect_tag_id],
    )
    hypothesis = UpgradeHypothesis(
        source_candidate_ids=[candidate.learning_candidate_id],
        target_surface=TargetSurface.VALIDATORS,
        affected_metric="first_pass_validation_rate",
        hypothesis="A stricter validator should reduce reviewer rework.",
        expected_direction="increase",
        risk_level="medium",
    )
    plan = ExperimentPlan(
        hypothesis_id=hypothesis.hypothesis_id,
        eval_suite_ref="evals/fixtures/classify_exception_cases.jsonl",
        baseline_ref="c5be37c",
        candidate_change_summary="Synthetic proposal-only validator change.",
        success_metrics=["first_pass_validation_rate"],
        failure_thresholds={"route_exact_match_rate": 1.0},
    )
    result = ShadowEvalResult(
        experiment_plan_id=plan.experiment_plan_id,
        baseline_metrics={"first_pass_validation_rate": 1.0},
        candidate_metrics={"first_pass_validation_rate": 1.0},
        metric_deltas={"first_pass_validation_rate": 0.0},
        recommended_next_action="request_human_review",
    )
    proposal = UpgradeProposal(
        hypothesis_id=hypothesis.hypothesis_id,
        experiment_plan_id=plan.experiment_plan_id,
        shadow_eval_result_id=result.shadow_eval_result_id,
        target_surface=TargetSurface.VALIDATORS,
        expected_metric_lift={"first_pass_validation_rate": 0.0},
        risks=["Synthetic proposal only; no automatic implementation."],
        tests_required=["python -m pytest"],
    )
    recommendation = ActionRecommendation(
        proposal_id=proposal.upgrade_proposal_id,
        action_type="draft_codex_task",
        target_surface=TargetSurface.VALIDATORS,
        risk_level="medium",
        rationale="Draft a human-reviewable Codex task.",
    )
    draft = CodexTaskDraft(
        recommendation_id=recommendation.action_recommendation_id,
        codex_level="High",
        allowed_paths=["src/lawfirm_os_orchestrator/policy/**", "tests/**"],
        forbidden_paths=["../LawFirm-os-semantic-substrate/**", "../LawFirm-os-exceptions-lake-runtime/**"],
        validation_commands=["python -m pytest"],
        stop_conditions=["Stop if real client or matter data is required."],
        prompt_markdown="Draft a proposal-only validator improvement for human review.",
    )
    return [defect, correction, pressure, candidate, hypothesis, plan, result, proposal, recommendation, draft]


def test_learning_models_round_trip_json():
    for model in sample_models():
        restored = type(model).model_validate_json(model.model_dump_json())
        assert restored == model


def test_learning_models_forbid_extra_fields():
    with pytest.raises(ValidationError):
        DefectTag.model_validate(
            {
                "category": "structural",
                "target_surface": "validators",
                "severity": "medium",
                "description": "Synthetic defect.",
                "unexpected": True,
            }
        )


def test_learning_models_reject_missing_required_fields():
    with pytest.raises(ValidationError):
        UpgradeHypothesis.model_validate(
            {
                "source_candidate_ids": ["candidate_001"],
                "target_surface": "validators",
                "affected_metric": "first_pass_validation_rate",
                "expected_direction": "increase",
                "risk_level": "medium",
            }
        )


def test_learning_models_reject_invalid_enums():
    with pytest.raises(ValidationError):
        DefectTag(
            category="structural",
            target_surface="canonical_route_ids",
            severity="medium",
            description="Forbidden target surface must not validate.",
        )


def test_learning_models_are_proposal_only_and_non_executing():
    for model in sample_models():
        flags = boundary_flags(model)
        assert flags == {
            "semantics": "proposal_only",
            "may_execute": False,
            "may_apply_patch": False,
            "may_push_git": False,
            "may_write_sibling_repo": False,
            "may_mutate_canon": False,
        }


def test_all_learning_models_use_strict_boundary_base():
    expected = {
        "DefectTag",
        "ReviewerCorrection",
        "PressureVector",
        "LearningCandidate",
        "UpgradeHypothesis",
        "ExperimentPlan",
        "ShadowEvalResult",
        "UpgradeProposal",
        "ActionRecommendation",
        "AlgorithmInsight",
        "CodexTaskDraft",
    }
    assert {model_type.__name__ for model_type in LEARNING_MODEL_TYPES} == expected


def test_codex_task_draft_rejects_forbidden_execution_language():
    with pytest.raises(ValidationError, match="forbidden execution language"):
        CodexTaskDraft(
            recommendation_id="recommendation_001",
            codex_level="High",
            allowed_paths=["src/**"],
            forbidden_paths=["../LawFirm-os-semantic-substrate/**"],
            validation_commands=["python -m pytest"],
            stop_conditions=["Stop if real data is required."],
            prompt_markdown="Implement and git push the change.",
        )
