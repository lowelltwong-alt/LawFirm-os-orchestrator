from __future__ import annotations

from typing import Literal

from pydantic import Field

from lawfirm_os_orchestrator.autonomy.autonomy_gate import (
    AutonomyDecision,
    LocalPhase2Model,
    RiskColor,
)
from lawfirm_os_orchestrator.harness.hardness_scorer import HardnessBand, HardnessScore
from lawfirm_os_orchestrator.harness.leverage_scorer import LeverageScore
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.time import utc_now


class HarnessPlan(LocalPhase2Model):
    harness_plan_id: str = Field(
        default_factory=lambda: new_id("harness_plan"), min_length=1
    )
    target_object_id: str = Field(min_length=1)
    risk_color: RiskColor
    hardness_level: int = Field(ge=0, le=5)
    leverage_score: float = Field(ge=0.0, le=1.0)
    harness_level: HardnessBand
    required_agents: list[str] = Field(default_factory=list)
    required_tests: list[str] = Field(min_length=1)
    allowed_outputs: list[str] = Field(min_length=1)
    forbidden_outputs: list[str] = Field(min_length=1)
    human_required: bool
    rollback_required: bool
    authority_source: Literal["risk_color"] = "risk_color"
    harness_depth_source: Literal["hardness"] = "hardness"
    priority_source: Literal["leverage"] = "leverage"
    reasons: list[str] = Field(min_length=1)
    created_at: str = Field(default_factory=utc_now)


def _band(level: int) -> HardnessBand:
    return HardnessBand(f"H{level}")


def _required_agents(level: int, risk_color: RiskColor) -> list[str]:
    if risk_color == RiskColor.RED:
        return ["planner", "evaluator", "adversarial_critic", "human_decision_owner"]
    if level >= 4:
        return ["planner", "builder", "evaluator", "adversarial_critic"]
    if level == 3:
        return ["planner", "builder", "evaluator"]
    if level == 2:
        return ["planner", "builder"]
    if level == 1:
        return ["builder"]
    return []


def _base_forbidden_outputs(risk_color: RiskColor) -> list[str]:
    forbidden = [
        "Semantic Substrate mutation",
        "canonical route_id or event_class creation",
        "real client or matter data handling",
        "external writes",
        "live model calls",
        "live Research Radar automation",
        "Git operations",
    ]
    if risk_color in {RiskColor.YELLOW, RiskColor.GREEN_CANDIDATE}:
        forbidden.append("final authority without human review")
        forbidden.append("green restoration")
    if risk_color == RiskColor.RED:
        forbidden.append("execution without explicit human approval")
    return forbidden


def select_harness(
    *,
    autonomy: AutonomyDecision,
    hardness: HardnessScore,
    leverage: LeverageScore,
) -> HarnessPlan:
    if autonomy.risk_color == RiskColor.RED:
        level = 5
        allowed_outputs = ["proposal-only risk memo", "human decision packet"]
        human_required = True
        rollback_required = True
        reasons = [
            "red risk color controls authority",
            "hard red requires human-required H5 harness",
        ]
    elif autonomy.risk_color == RiskColor.YELLOW:
        level = max(2, min(4, hardness.hardness_level))
        if leverage.leverage_score >= 0.66:
            level = min(4, max(level, 4))
        allowed_outputs = [
            "local draft artifact",
            "test evidence",
            "human review packet",
            "green-candidate recommendation",
        ]
        human_required = True
        rollback_required = level >= 3
        reasons = ["yellow risk color requires review before final authority"]
    else:
        level = min(max(hardness.hardness_level, 0), 5)
        if leverage.leverage_score >= 0.66 and level < 2:
            level = 2
        allowed_outputs = ["local reversible artifact", "local audit evidence"]
        human_required = False
        rollback_required = level >= 3
        reasons = ["green authority remains limited to preapproved lane"]
    reasons.extend(
        [
            "hardness controls harness depth only",
            "leverage controls priority only",
            "risk color controls authority",
        ]
    )
    return HarnessPlan(
        target_object_id=autonomy.autonomy_decision_id,
        risk_color=autonomy.risk_color,
        hardness_level=hardness.hardness_level,
        leverage_score=leverage.leverage_score,
        harness_level=_band(level),
        required_agents=_required_agents(level, autonomy.risk_color),
        required_tests=[
            "python scripts/run_full_pytest.py",
            "python scripts/check_safety.py --stdout json",
        ],
        allowed_outputs=allowed_outputs,
        forbidden_outputs=_base_forbidden_outputs(autonomy.risk_color),
        human_required=human_required,
        rollback_required=rollback_required,
        reasons=reasons,
    )
