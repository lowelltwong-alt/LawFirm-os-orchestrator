from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any

from pydantic import Field

from lawfirm_os_orchestrator.autonomy.autonomy_gate import LocalPhase2Model, RiskColor
from lawfirm_os_orchestrator.research.research_signal_ingest import ResearchSignal
from lawfirm_os_orchestrator.util.json_io import read_json


class AssumptionStatus(StrEnum):
    VALID = "valid"
    UNCERTAIN = "uncertain"
    WEAKENED = "weakened"
    REQUIRES_REVIEW = "requires_review"
    INVALID = "invalid"


class AssumptionRecord(LocalPhase2Model):
    assumption_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    status: AssumptionStatus = AssumptionStatus.VALID
    keywords: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)


class GreenLanePassport(LocalPhase2Model):
    lane_id: str = Field(min_length=1)
    risk_color: RiskColor = RiskColor.GREEN
    description: str = Field(min_length=1)
    assumptions: list[AssumptionRecord] = Field(min_length=1)
    source_refs: list[str] = Field(default_factory=list)
    preapproved: bool = True


class AssumptionSignalMapping(LocalPhase2Model):
    lane_id: str = Field(min_length=1)
    assumption_id: str = Field(min_length=1)
    signal_id: str = Field(min_length=1)
    match_reasons: list[str] = Field(min_length=1)


def _records(raw: Any, key: str) -> list[Any]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        value = raw.get(key)
        if isinstance(value, list):
            return value
        if "lane_id" in raw:
            return [raw]
    raise ValueError(f"expected a lane object, list, or object with {key}")


def load_green_lanes(path: Path) -> list[GreenLanePassport]:
    return [GreenLanePassport.model_validate(item) for item in _records(read_json(path), "lanes")]


def map_signal_to_assumptions(lane: GreenLanePassport, signal: ResearchSignal) -> list[AssumptionSignalMapping]:
    mappings: list[AssumptionSignalMapping] = []
    explicit = set(signal.affected_assumption_ids)
    signal_terms = {term.lower() for term in signal.keywords}
    signal_terms.update(signal.summary.lower().replace(",", " ").replace(".", " ").split())
    for assumption in lane.assumptions:
        reasons: list[str] = []
        if assumption.assumption_id in explicit:
            reasons.append("signal explicitly references assumption")
        assumption_terms = {term.lower() for term in assumption.keywords}
        overlap = sorted(signal_terms & assumption_terms)
        if overlap:
            reasons.append(f"keyword overlap: {', '.join(overlap)}")
        if reasons:
            mappings.append(
                AssumptionSignalMapping(
                    lane_id=lane.lane_id,
                    assumption_id=assumption.assumption_id,
                    signal_id=signal.signal_id,
                    match_reasons=reasons,
                )
            )
    return mappings


def map_signals_to_assumptions(
    *,
    lane: GreenLanePassport,
    signals: list[ResearchSignal],
) -> list[AssumptionSignalMapping]:
    mappings: list[AssumptionSignalMapping] = []
    for signal in signals:
        mappings.extend(map_signal_to_assumptions(lane, signal))
    return mappings
