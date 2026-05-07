from __future__ import annotations

from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

from pydantic import Field

from lawfirm_os_orchestrator.autonomy.autonomy_gate import LocalPhase2Model
from lawfirm_os_orchestrator.util.json_io import read_json


class SignalType(StrEnum):
    ASSUMPTION_UNCERTAINTY = "assumption_uncertainty"
    EXTERNAL_AI_INCIDENT = "external_ai_incident"
    USER_BEHAVIOR_DRIFT = "user_behavior_drift"
    INPUT_DISTRIBUTION_DRIFT = "input_distribution_drift"
    EVAL_DRIFT = "eval_drift"
    REVIEWER_EDIT_DRIFT = "reviewer_edit_drift"
    PROVENANCE_UNCLEAR = "provenance_unclear"
    RESEARCH_UPDATE = "research_update"
    CONFIG_REGISTRY_DRIFT = "config_registry_drift"
    LOCAL_MIRROR_STALE = "local_mirror_stale"
    BLAST_RADIUS_EXPANSION = "blast_radius_expansion"
    HARD_RED_TRIGGER = "hard_red_trigger"
    INFORMATIONAL = "informational"


class ResearchSignal(LocalPhase2Model):
    signal_id: str = Field(min_length=1)
    signal_type: SignalType
    summary: str = Field(min_length=1)
    affected_assumption_ids: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    hard_red_triggers: list[str] = Field(default_factory=list)
    yellow_triggers: list[str] = Field(default_factory=list)
    indicates_green_restoration: bool = False
    evidence_refs: list[str] = Field(default_factory=list)
    source_refs: list[str] = Field(default_factory=list)
    local_only: Literal[True] = True
    no_network_required: Literal[True] = True


def _records(raw: Any, key: str) -> list[Any]:
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        value = raw.get(key)
        if isinstance(value, list):
            return value
        if "signal_id" in raw:
            return [raw]
    raise ValueError(f"expected a signal object, list, or object with {key}")


def load_research_signals(path: Path) -> list[ResearchSignal]:
    return [ResearchSignal.model_validate(item) for item in _records(read_json(path), "signals")]
