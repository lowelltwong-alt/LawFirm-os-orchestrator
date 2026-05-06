from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from lawfirm_os_orchestrator.learning.models import ActionRecommendation, TargetSurface, boundary_flags


class ActionRecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal["1.0"] = "1.0"
    proposal_id: str = Field(min_length=1)
    action_type: Literal["request_human_review", "run_shadow_eval", "revise_hypothesis", "draft_codex_task", "reject_candidate"]
    target_surface: TargetSurface
    risk_level: Literal["low", "medium", "high", "critical"]
    rationale: str = Field(min_length=1)
    recommended_effort_level: Literal["Low", "Medium", "High", "Extra High"]


def build_action_recommendation(request: ActionRecommendationRequest) -> dict[str, object]:
    recommendation = ActionRecommendation(
        proposal_id=request.proposal_id,
        action_type=request.action_type,
        target_surface=request.target_surface,
        risk_level=request.risk_level,
        rationale=request.rationale,
    )
    return {
        "schema_version": "1.0",
        "semantics": "proposal_only",
        "recommended_effort_level": request.recommended_effort_level,
        "recommendation": recommendation.model_dump(mode="json"),
        "boundary_flags": boundary_flags(recommendation),
        "local_artifact_only": True,
        "runs_codex": False,
        "runs_git": False,
        "applies_patch": False,
    }
