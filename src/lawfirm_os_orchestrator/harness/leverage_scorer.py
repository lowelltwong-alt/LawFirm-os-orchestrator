from __future__ import annotations

from typing import Literal

from pydantic import Field

from lawfirm_os_orchestrator.autonomy.autonomy_gate import LocalPhase2Model
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.time import utc_now


class OpportunityScorecard(LocalPhase2Model):
    scorecard_id: str = Field(min_length=1)
    impact: float = Field(ge=0.0, le=1.0)
    recurrence: float = Field(ge=0.0, le=1.0)
    strategic_alignment: float = Field(ge=0.0, le=1.0)
    time_value: float = Field(ge=0.0, le=1.0)
    review_rework_reduction: float = Field(ge=0.0, le=1.0)
    learning_value: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    effort: float = Field(ge=0.0, le=1.0)
    risk: float = Field(ge=0.0, le=1.0)
    dependency: float = Field(ge=0.0, le=1.0)
    governance_load: float = Field(ge=0.0, le=1.0)


class LeverageScore(LocalPhase2Model):
    leverage_score_id: str = Field(default_factory=lambda: new_id("leverage_score"), min_length=1)
    scorecard_id: str = Field(min_length=1)
    formula: str
    leverage_score: float = Field(ge=0.0, le=1.0)
    priority_band: Literal["low", "medium", "high"]
    inputs: dict[str, float]
    controls_priority_only: Literal[True] = True
    created_at: str = Field(default_factory=utc_now)


FORMULA = (
    "clamp((0.20*impact + 0.15*recurrence + 0.15*strategic_alignment + "
    "0.10*time_value + 0.10*review_rework_reduction + 0.10*learning_value + "
    "0.10*confidence) - (0.04*effort + 0.03*risk + 0.02*dependency + "
    "0.01*governance_load), 0, 1)"
)


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def score_leverage(scorecard: OpportunityScorecard) -> LeverageScore:
    scoring_inputs = {
        "impact": scorecard.impact,
        "recurrence": scorecard.recurrence,
        "strategic_alignment": scorecard.strategic_alignment,
        "time_value": scorecard.time_value,
        "review_rework_reduction": scorecard.review_rework_reduction,
        "learning_value": scorecard.learning_value,
        "confidence": scorecard.confidence,
        "effort": scorecard.effort,
        "risk": scorecard.risk,
        "dependency": scorecard.dependency,
        "governance_load": scorecard.governance_load,
    }
    positive = (
        0.20 * scorecard.impact
        + 0.15 * scorecard.recurrence
        + 0.15 * scorecard.strategic_alignment
        + 0.10 * scorecard.time_value
        + 0.10 * scorecard.review_rework_reduction
        + 0.10 * scorecard.learning_value
        + 0.10 * scorecard.confidence
    )
    friction = (
        0.04 * scorecard.effort
        + 0.03 * scorecard.risk
        + 0.02 * scorecard.dependency
        + 0.01 * scorecard.governance_load
    )
    score = round(_clamp(positive - friction), 6)
    if score >= 0.66:
        band: Literal["low", "medium", "high"] = "high"
    elif score >= 0.33:
        band = "medium"
    else:
        band = "low"
    return LeverageScore(
        scorecard_id=scorecard.scorecard_id,
        formula=FORMULA,
        leverage_score=score,
        priority_band=band,
        inputs=scoring_inputs,
    )
