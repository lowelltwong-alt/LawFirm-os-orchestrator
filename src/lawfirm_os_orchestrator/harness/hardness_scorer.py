from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field

from lawfirm_os_orchestrator.autonomy.autonomy_gate import ActionDescriptor, ActionType, LocalPhase2Model
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.time import utc_now


class HardnessBand(StrEnum):
    H0 = "H0"
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"
    H5 = "H5"


class HardnessScore(LocalPhase2Model):
    hardness_score_id: str = Field(default_factory=lambda: new_id("hardness_score"), min_length=1)
    action_id: str = Field(min_length=1)
    hardness_level: int = Field(ge=0, le=5)
    hardness_band: HardnessBand
    summary: str = Field(min_length=1)
    reasons: list[str] = Field(min_length=1)
    controls_harness_depth_only: Literal[True] = True
    created_at: str = Field(default_factory=utc_now)


def score_hardness(action: ActionDescriptor) -> HardnessScore:
    if action.action_type == ActionType.DETERMINISTIC_CHECK and action.reversible and action.local_only:
        level = 0
        summary = "deterministic/doc-only trivial check"
    elif action.action_type in {ActionType.LOCAL_ARTIFACT_GENERATION, ActionType.CODEX_TASK_PACKET_DRAFT}:
        level = 1
        summary = "simple local artifact generation"
    elif action.action_type in {ActionType.DOC_CHANGE, ActionType.TEST_CHANGE}:
        level = 2
        summary = "moderate schema/doc/test implementation"
    elif action.action_type in {ActionType.PROMPT_CHANGE, ActionType.VALIDATOR_CHANGE, ActionType.CODE_CHANGE}:
        level = 3
        summary = "bounded behavior change requiring tests"
    elif action.action_type == ActionType.AUTONOMY_CHANGE:
        level = 4
        summary = "ambiguous or high-leverage autonomy change requiring evaluator/critic review"
    else:
        level = 5
        summary = "high-ambiguity or high-blast-radius adjacent work"
    if not action.reversible and level < 4:
        level = 4
        summary = "non-reversible work requires evaluator/critic review"
    if not action.local_only:
        level = 5
        summary = "non-local work requires full harness and human decision packet"
    return HardnessScore(
        action_id=action.action_id,
        hardness_level=level,
        hardness_band=HardnessBand(f"H{level}"),
        summary=summary,
        reasons=[summary, "hardness controls harness depth only"],
    )
