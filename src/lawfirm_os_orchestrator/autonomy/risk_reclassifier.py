from __future__ import annotations

from typing import Literal

from pydantic import Field

from lawfirm_os_orchestrator.autonomy.assumption_mapper import (
    AssumptionSignalMapping,
    AssumptionStatus,
    GreenLanePassport,
)
from lawfirm_os_orchestrator.autonomy.autonomy_gate import LocalPhase2Model, RiskColor
from lawfirm_os_orchestrator.autonomy.red_flag_detector import hard_red_triggers
from lawfirm_os_orchestrator.research.research_signal_ingest import ResearchSignal, SignalType
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.time import utc_now

YELLOW_SIGNAL_TYPES: frozenset[SignalType] = frozenset(
    {
        SignalType.ASSUMPTION_UNCERTAINTY,
        SignalType.EXTERNAL_AI_INCIDENT,
        SignalType.USER_BEHAVIOR_DRIFT,
        SignalType.INPUT_DISTRIBUTION_DRIFT,
        SignalType.EVAL_DRIFT,
        SignalType.REVIEWER_EDIT_DRIFT,
        SignalType.PROVENANCE_UNCLEAR,
        SignalType.RESEARCH_UPDATE,
        SignalType.CONFIG_REGISTRY_DRIFT,
        SignalType.LOCAL_MIRROR_STALE,
        SignalType.BLAST_RADIUS_EXPANSION,
    }
)

YELLOW_ASSUMPTION_STATUSES: frozenset[AssumptionStatus] = frozenset(
    {
        AssumptionStatus.UNCERTAIN,
        AssumptionStatus.WEAKENED,
        AssumptionStatus.REQUIRES_REVIEW,
    }
)


class GreenLaneWatchResult(LocalPhase2Model):
    evaluation_id: str = Field(default_factory=lambda: new_id("green_lane_watch"), min_length=1)
    evaluated_at: str = Field(default_factory=utc_now)
    lane_id: str = Field(min_length=1)
    previous_color: RiskColor
    recommended_color: RiskColor
    reclassification_reason: str = Field(min_length=1)
    affected_assumptions: list[str] = Field(default_factory=list)
    trigger_signals: list[str] = Field(default_factory=list)
    hard_red_triggers: list[str] = Field(default_factory=list)
    yellow_triggers: list[str] = Field(default_factory=list)
    explanation: str = Field(min_length=1)
    allowed_next_actions: list[str] = Field(min_length=1)
    forbidden_next_actions: list[str] = Field(min_length=1)
    human_restoration_required: Literal[True] = True
    may_restore_green: Literal[False] = False
    evidence_refs: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


def _signals_by_id(signals: list[ResearchSignal]) -> dict[str, ResearchSignal]:
    return {signal.signal_id: signal for signal in signals}


def reclassify_lane(
    *,
    lane: GreenLanePassport,
    signals: list[ResearchSignal],
    mappings: list[AssumptionSignalMapping],
) -> GreenLaneWatchResult:
    matched_signal_ids = sorted({mapping.signal_id for mapping in mappings})
    matched_assumption_ids = sorted({mapping.assumption_id for mapping in mappings})
    relevant_signals = [_signals_by_id(signals)[signal_id] for signal_id in matched_signal_ids]
    hard_red = sorted({trigger for signal in relevant_signals for trigger in hard_red_triggers(signal)})
    yellow: set[str] = set()
    assumptions_by_id = {assumption.assumption_id: assumption for assumption in lane.assumptions}
    for assumption_id in matched_assumption_ids:
        status = assumptions_by_id[assumption_id].status
        if status in YELLOW_ASSUMPTION_STATUSES:
            yellow.add(f"assumption_{status.value}")
    for signal in relevant_signals:
        yellow.update(signal.yellow_triggers)
        if signal.signal_type in YELLOW_SIGNAL_TYPES:
            yellow.add(signal.signal_type.value)
    evidence_refs = sorted({ref for signal in relevant_signals for ref in signal.evidence_refs})
    source_refs = sorted(set(lane.source_refs) | {ref for signal in relevant_signals for ref in signal.source_refs})
    if hard_red:
        return GreenLaneWatchResult(
            lane_id=lane.lane_id,
            previous_color=lane.risk_color,
            recommended_color=RiskColor.RED,
            reclassification_reason="hard red trigger detected",
            affected_assumptions=matched_assumption_ids,
            trigger_signals=matched_signal_ids,
            hard_red_triggers=hard_red,
            yellow_triggers=sorted(yellow),
            explanation=(
                f"Lane {lane.lane_id} must downgrade to red because signals "
                f"{', '.join(matched_signal_ids)} affected assumptions "
                f"{', '.join(matched_assumption_ids)} and triggered {', '.join(hard_red)}."
            ),
            allowed_next_actions=["prepare proposal-only risk memo", "prepare human decision packet"],
            forbidden_next_actions=[
                "restore green automatically",
                "execute final authority",
                "write Semantic Substrate",
                "write Exception Lake",
                "call network or models",
            ],
            evidence_refs=evidence_refs,
            source_refs=source_refs,
        )
    if yellow:
        return GreenLaneWatchResult(
            lane_id=lane.lane_id,
            previous_color=lane.risk_color,
            recommended_color=RiskColor.YELLOW,
            reclassification_reason="assumption drift requires review",
            affected_assumptions=matched_assumption_ids,
            trigger_signals=matched_signal_ids,
            hard_red_triggers=[],
            yellow_triggers=sorted(yellow),
            explanation=(
                f"Lane {lane.lane_id} should downgrade to yellow because signals "
                f"{', '.join(matched_signal_ids)} affected assumptions "
                f"{', '.join(matched_assumption_ids)} with yellow triggers {', '.join(sorted(yellow))}."
            ),
            allowed_next_actions=["prepare review packet", "recommend green-candidate after human review"],
            forbidden_next_actions=[
                "restore green automatically",
                "finalize authority without human review",
                "write Semantic Substrate",
                "write Exception Lake",
                "call network or models",
            ],
            evidence_refs=evidence_refs,
            source_refs=source_refs,
        )
    return GreenLaneWatchResult(
        lane_id=lane.lane_id,
        previous_color=lane.risk_color,
        recommended_color=lane.risk_color,
        reclassification_reason="no affected assumptions changed",
        affected_assumptions=[],
        trigger_signals=[],
        hard_red_triggers=[],
        yellow_triggers=[],
        explanation=f"Lane {lane.lane_id} remains {lane.risk_color.value}; no signal affected an assumption.",
        allowed_next_actions=["continue within existing preapproved lane assumptions"],
        forbidden_next_actions=[
            "restore green automatically",
            "expand green authority",
            "write Semantic Substrate",
            "write Exception Lake",
            "call network or models",
        ],
        evidence_refs=[],
        source_refs=lane.source_refs,
    )
