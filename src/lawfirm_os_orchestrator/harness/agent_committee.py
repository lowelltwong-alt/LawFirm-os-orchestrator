from __future__ import annotations

from typing import Literal

from pydantic import Field

from lawfirm_os_orchestrator.autonomy.autonomy_gate import LocalPhase2Model, RiskColor
from lawfirm_os_orchestrator.harness.hardness_scorer import HardnessBand
from lawfirm_os_orchestrator.util.ids import new_id


class AgentReviewPlan(LocalPhase2Model):
    review_plan_id: str = Field(default_factory=lambda: new_id("agent_review_plan"), min_length=1)
    required_review_roles: list[str] = Field(min_length=1)
    hard_veto_roles: list[str] = Field(default_factory=list)
    quorum_rule: str = Field(min_length=1)
    review_scope: list[str] = Field(min_length=1)
    allowed_review_outputs: list[str] = Field(min_length=1)
    forbidden_review_outputs: list[str] = Field(min_length=1)
    human_decision_required: bool
    source_refs: list[str] = Field(default_factory=list)
    inert_review_plan_only: Literal[True] = True


def build_agent_review_plan(
    *,
    risk_color: RiskColor,
    harness_level: HardnessBand,
    source_refs: list[str],
) -> AgentReviewPlan:
    if risk_color == RiskColor.RED:
        roles = ["planner", "evaluator", "adversarial_critic", "human_decision_owner"]
        veto = ["human_decision_owner", "adversarial_critic"]
        quorum = "human decision owner plus no hard veto"
        human_required = True
    elif risk_color == RiskColor.YELLOW or harness_level in {HardnessBand.H4, HardnessBand.H5}:
        roles = ["planner", "builder", "evaluator", "adversarial_critic"]
        veto = ["evaluator", "adversarial_critic"]
        quorum = "two approving review roles and no hard veto"
        human_required = True
    elif harness_level in {HardnessBand.H2, HardnessBand.H3}:
        roles = ["planner", "builder", "evaluator"]
        veto = ["evaluator"]
        quorum = "builder plus evaluator review"
        human_required = False
    else:
        roles = ["builder"]
        veto = []
        quorum = "single builder self-check"
        human_required = False
    return AgentReviewPlan(
        required_review_roles=roles,
        hard_veto_roles=veto,
        quorum_rule=quorum,
        review_scope=["authority limits", "safety invariants", "validation evidence", "rollback rule"],
        allowed_review_outputs=["review notes", "risk memo", "human decision packet", "green-candidate recommendation"],
        forbidden_review_outputs=[
            "execute Codex",
            "execute Git",
            "apply patches",
            "call models",
            "call network",
            "write Semantic Substrate",
            "write Exception Lake",
            "restore green authority",
        ],
        human_decision_required=human_required,
        source_refs=source_refs,
    )
