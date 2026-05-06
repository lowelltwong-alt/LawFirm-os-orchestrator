from __future__ import annotations

from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.time import utc_now


class LearningModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    semantics: Literal["proposal_only"] = "proposal_only"
    may_execute: Literal[False] = False
    may_apply_patch: Literal[False] = False
    may_push_git: Literal[False] = False
    may_write_sibling_repo: Literal[False] = False
    may_mutate_canon: Literal[False] = False


class TargetSurface(StrEnum):
    EVALS = "evals"
    PROMPT_TEMPLATES = "prompt_templates"
    MODEL_ROUTING = "model_routing"
    VALIDATORS = "validators"
    CONFIDENCE_CALIBRATION = "confidence_calibration"
    EVIDENCE_PACKET_BUILDER = "evidence_packet_builder"
    APPROVAL_THRESHOLDS = "approval_thresholds"
    LEDGER_OBSERVABILITY_FIELDS = "ledger_observability_fields"
    RESEARCH_RADAR_SCORING = "research_radar_scoring"
    LEARNING_LOOP = "learning_loop"
    CODEX_TASK_DRAFTS = "codex_task_drafts"


class MethodCategory(StrEnum):
    EVALUATOR_GUIDED_SEARCH = "evaluator_guided_search"
    VERIFIER_GUIDED_VALIDATION = "verifier_guided_validation"
    RETRIEVAL_RANKING = "retrieval_ranking"
    CONFIDENCE_CALIBRATION = "confidence_calibration"
    MODEL_ROUTING = "model_routing"
    OBSERVABILITY = "observability"
    OTHER = "other"


class DefectCategory(StrEnum):
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    PROVENANCE = "provenance"
    LINEAGE = "lineage"
    GOVERNANCE = "governance"
    PRIVACY = "privacy"
    TEMPORAL_STALE_CONTRACT = "temporal_stale_contract"
    DUPLICATION = "duplication"
    RETRY_BUDGET = "retry_budget"
    TOOL = "tool"
    MODEL = "model"
    AUDIT = "audit"


class DefectTag(LearningModel):
    defect_tag_id: str = Field(default_factory=lambda: new_id("defect_tag"), min_length=1)
    category: DefectCategory
    target_surface: TargetSurface
    severity: Literal["low", "medium", "high", "critical"]
    description: str = Field(min_length=1)
    evidence_refs: list[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)


class ReviewerCorrection(LearningModel):
    correction_id: str = Field(default_factory=lambda: new_id("reviewer_correction"), min_length=1)
    run_id: str = Field(min_length=1)
    reviewer_ref: str = Field(min_length=1)
    original_route_id: str = Field(min_length=1)
    corrected_route_id: str = Field(min_length=1)
    original_event_class: str = Field(min_length=1)
    corrected_event_class: str = Field(min_length=1)
    defect_tags: list[DefectTag] = Field(default_factory=list)
    rationale: str = Field(min_length=1)
    created_at: str = Field(default_factory=utc_now)


class PressureVector(LearningModel):
    pressure_vector_id: str = Field(default_factory=lambda: new_id("pressure_vector"), min_length=1)
    target_surface: TargetSurface
    defect_tags: list[DefectTag] = Field(min_length=1)
    recurrence_count: int = Field(ge=1)
    impact: float = Field(ge=0.0, le=1.0)
    detectability: float = Field(ge=0.0, le=1.0)
    candidate_causes: list[str] = Field(min_length=1)
    smallest_plausible_intervention: str = Field(min_length=1)
    status: Literal["candidate", "under_review", "rejected", "accepted_for_experiment"] = "candidate"
    created_at: str = Field(default_factory=utc_now)


class LearningCandidate(LearningModel):
    learning_candidate_id: str = Field(default_factory=lambda: new_id("learning_candidate"), min_length=1)
    candidate_type: Literal["run_level", "pressure_vector", "eval", "governance", "research_signal"]
    source_refs: list[str] = Field(min_length=1)
    target_surface: TargetSurface
    summary: str = Field(min_length=1)
    pressure_vector_id: str | None = None
    defect_tag_ids: list[str] = Field(default_factory=list)
    status: Literal["candidate", "under_review", "rejected", "promoted_to_hypothesis"] = "candidate"
    created_at: str = Field(default_factory=utc_now)


class UpgradeHypothesis(LearningModel):
    hypothesis_id: str = Field(default_factory=lambda: new_id("upgrade_hypothesis"), min_length=1)
    source_candidate_ids: list[str] = Field(min_length=1)
    target_surface: TargetSurface
    affected_metric: str = Field(min_length=1)
    hypothesis: str = Field(min_length=1)
    expected_direction: Literal["increase", "decrease", "stabilize"]
    risk_level: Literal["low", "medium", "high", "critical"]
    created_at: str = Field(default_factory=utc_now)


class ExperimentPlan(LearningModel):
    experiment_plan_id: str = Field(default_factory=lambda: new_id("experiment_plan"), min_length=1)
    hypothesis_id: str = Field(min_length=1)
    eval_suite_ref: str = Field(min_length=1)
    baseline_ref: str = Field(min_length=1)
    candidate_change_summary: str = Field(min_length=1)
    success_metrics: list[str] = Field(min_length=1)
    failure_thresholds: dict[str, float] = Field(default_factory=dict)
    shadow_eval_required: Literal[True] = True
    created_at: str = Field(default_factory=utc_now)


class ShadowEvalResult(LearningModel):
    shadow_eval_result_id: str = Field(default_factory=lambda: new_id("shadow_eval_result"), min_length=1)
    experiment_plan_id: str = Field(min_length=1)
    baseline_metrics: dict[str, float]
    candidate_metrics: dict[str, float]
    metric_deltas: dict[str, float] = Field(default_factory=dict)
    regression_warnings: list[str] = Field(default_factory=list)
    recommended_next_action: Literal["reject", "revise", "draft_proposal", "request_human_review"]
    created_at: str = Field(default_factory=utc_now)


class UpgradeProposal(LearningModel):
    upgrade_proposal_id: str = Field(default_factory=lambda: new_id("upgrade_proposal"), min_length=1)
    hypothesis_id: str = Field(min_length=1)
    experiment_plan_id: str = Field(min_length=1)
    shadow_eval_result_id: str | None = None
    target_surface: TargetSurface
    expected_metric_lift: dict[str, float]
    risks: list[str] = Field(min_length=1)
    tests_required: list[str] = Field(min_length=1)
    approval_required: Literal[True] = True
    implementation_allowed: Literal[False] = False
    created_at: str = Field(default_factory=utc_now)


class ActionRecommendation(LearningModel):
    action_recommendation_id: str = Field(default_factory=lambda: new_id("action_recommendation"), min_length=1)
    proposal_id: str = Field(min_length=1)
    action_type: Literal["request_human_review", "run_shadow_eval", "revise_hypothesis", "draft_codex_task", "reject_candidate"]
    target_surface: TargetSurface
    risk_level: Literal["low", "medium", "high", "critical"]
    rationale: str = Field(min_length=1)
    created_at: str = Field(default_factory=utc_now)


class AlgorithmInsight(LearningModel):
    algorithm_insight_id: str = Field(default_factory=lambda: new_id("algorithm_insight"), min_length=1)
    source_ref: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    method_category: MethodCategory
    target_surface: TargetSurface
    affected_metric: str = Field(min_length=1)
    credibility: float = Field(ge=0.0, le=1.0)
    relevance: float = Field(ge=0.0, le=1.0)
    expected_lift: float = Field(ge=0.0, le=1.0)
    verifiability: float = Field(ge=0.0, le=1.0)
    risk: float = Field(gt=0.0, le=1.0)
    implementation_cost: float = Field(gt=0.0, le=1.0)
    experiment_plan_ref: str | None = None
    created_at: str = Field(default_factory=utc_now)


class CodexTaskDraft(LearningModel):
    codex_task_draft_id: str = Field(default_factory=lambda: new_id("codex_task_draft"), min_length=1)
    recommendation_id: str = Field(min_length=1)
    codex_level: Literal["Low", "Medium", "High", "Extra High"]
    route: str = Field(min_length=1)
    mode: str = Field(min_length=1)
    allowed_paths: list[str] = Field(min_length=1)
    forbidden_paths: list[str] = Field(min_length=1)
    validation_commands: list[str] = Field(min_length=1)
    stop_conditions: list[str] = Field(min_length=1)
    expected_artifacts: list[str] = Field(min_length=1)
    prompt_markdown: str = Field(min_length=1)
    created_at: str = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def reject_execution_language(self) -> "CodexTaskDraft":
        forbidden_phrases = (
            "git push",
            "git merge",
            "git reset --hard",
            "write to semantic substrate",
            "modify semantic substrate",
            "write sibling repo",
            "modify sibling repo",
            "apply patch automatically",
            "execute automatically",
        )
        haystack = " ".join(
            [
                self.prompt_markdown,
                self.route,
                self.mode,
                " ".join(self.allowed_paths),
                " ".join(self.forbidden_paths),
                " ".join(self.validation_commands),
                " ".join(self.stop_conditions),
                " ".join(self.expected_artifacts),
            ]
        ).lower()
        matches = [phrase for phrase in forbidden_phrases if phrase in haystack]
        if matches:
            raise ValueError(f"CodexTaskDraft contains forbidden execution language: {', '.join(matches)}")
        return self


LEARNING_MODEL_TYPES: tuple[type[LearningModel], ...] = (
    DefectTag,
    ReviewerCorrection,
    PressureVector,
    LearningCandidate,
    UpgradeHypothesis,
    ExperimentPlan,
    ShadowEvalResult,
    UpgradeProposal,
    ActionRecommendation,
    AlgorithmInsight,
    CodexTaskDraft,
)


def boundary_flags(model: LearningModel) -> dict[str, Any]:
    return {
        "semantics": model.semantics,
        "may_execute": model.may_execute,
        "may_apply_patch": model.may_apply_patch,
        "may_push_git": model.may_push_git,
        "may_write_sibling_repo": model.may_write_sibling_repo,
        "may_mutate_canon": model.may_mutate_canon,
    }
