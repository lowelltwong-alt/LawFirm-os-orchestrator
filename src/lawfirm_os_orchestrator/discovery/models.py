from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import Field

from lawfirm_os_orchestrator.learning.models import LearningModel, TargetSurface
from lawfirm_os_orchestrator.util.ids import new_id


class SourceKind(StrEnum):
    PAPER = "paper"
    BENCHMARK = "benchmark"
    LAB_BLOG = "lab_blog"
    STANDARD = "standard"
    REPOSITORY = "repository"
    HUMAN_NOTE = "human_note"


class ClaimType(StrEnum):
    ALGORITHMIC_PATTERN = "algorithmic_pattern"
    EVALUATION_METHOD = "evaluation_method"
    GOVERNANCE_PATTERN = "governance_pattern"
    EVIDENCE_PATTERN = "evidence_pattern"
    HUMAN_NOTE = "human_note"


class EvidenceStrength(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    MEDIUM_HIGH = "medium_high"
    HIGH = "high"


class RecommendedAction(StrEnum):
    CREATE_SHADOW_EXPERIMENT = "create_shadow_experiment"
    CREATE_UPGRADE_HYPOTHESIS = "create_upgrade_hypothesis"
    ARCHIVE_FOR_REVIEW = "archive_for_review"
    NO_ACTION = "no_action"


class DiscoveryClaim(LearningModel):
    claim: str = Field(min_length=1)
    claim_type: ClaimType
    evidence_strength: EvidenceStrength


class DiscoveryRelevance(LearningModel):
    target_surfaces: list[TargetSurface] = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)
    possible_upgrade: str = Field(min_length=1)
    risk: str = Field(min_length=1)


class DiscoverySignal(LearningModel):
    signal_id: str = Field(default_factory=lambda: new_id("discovery_signal"), min_length=1)
    signal_type: Literal["external_research_discovery"]
    source_kind: SourceKind
    source_tier: int = Field(ge=1, le=4)
    source_uri: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    source_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    title: str = Field(min_length=1)
    published_at: str | None = None
    imported_at: str = Field(min_length=1)
    credibility: float = Field(ge=0.0, le=1.0)
    claims: list[DiscoveryClaim] = Field(min_length=1)
    relevance: DiscoveryRelevance
    recommended_action: RecommendedAction
    local_only: Literal[True] = True
    no_network_required: Literal[True] = True
    may_run_git: Literal[False] = False
    may_edit_code: Literal[False] = False
