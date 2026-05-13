from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class WorkflowDataClassification(StrictModel):
    contains_real_client_data: bool = False
    contains_real_matter_data: bool = False
    contains_privileged_content: bool = False
    redaction_status: Literal["synthetic", "redacted", "pending", "not_required"] = "synthetic"

    @model_validator(mode="after")
    def enforce_seed_boundary(self) -> "WorkflowDataClassification":
        if self.contains_real_client_data or self.contains_real_matter_data or self.contains_privileged_content:
            raise ValueError("Workflow Atlas seed accepts synthetic/redacted non-privileged intakes only")
        return self


class WorkflowIntakeSession(StrictModel):
    intake_session_id: str
    schema_type: Literal["workflow-intake-session"] = "workflow-intake-session"
    schema_version: Literal["v1"] = "v1"
    topic: str = Field(min_length=3)
    source_type: Literal[
        "teams_transcript",
        "voice_transcript",
        "manual_transcript",
        "typed_note",
        "screen_observation_future",
    ] = "manual_transcript"
    speaker_role: str = Field(min_length=1)
    speaker_job_key: str | None = None
    transcript_ref: str
    transcript_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    transcript_excerpt: str
    data_classification: WorkflowDataClassification = Field(default_factory=WorkflowDataClassification)
    status: Literal["captured", "extracted", "reviewed", "archived"] = "captured"


class WorkflowStep(StrictModel):
    step_id: str
    actor_role: str
    activity: str
    system: str | None = None
    input_artifacts: list[str] = Field(default_factory=list)
    output_artifacts: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(default_factory=list)
    exceptions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class DecisionPoint(StrictModel):
    decision_id: str
    question: str
    paths: list[str] = Field(default_factory=list)


class ExceptionPoint(StrictModel):
    exception_label: str
    candidate_exception_class: str
    impacts: list[str] = Field(default_factory=list)


class WorkflowFragment(StrictModel):
    workflow_fragment_id: str
    schema_type: Literal["workflow-fragment"] = "workflow-fragment"
    schema_version: Literal["v1"] = "v1"
    title: str
    status: Literal["draft", "corrected", "reviewed", "approved_candidate", "canonicalized", "superseded"] = "draft"
    source_intake_ids: list[str] = Field(min_length=1)
    trigger: str
    roles: list[str] = Field(default_factory=list)
    systems: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)
    steps: list[WorkflowStep] = Field(default_factory=list)
    decision_points: list[DecisionPoint] = Field(default_factory=list)
    exception_points: list[ExceptionPoint] = Field(default_factory=list)
    handoffs: list[str] = Field(default_factory=list)
    metrics_affected: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    confidence: dict[str, float] = Field(default_factory=dict)
    human_review_required: bool = True
    authority_boundary: dict[str, bool] = Field(default_factory=lambda: {
        "candidate_only": True,
        "no_canonical_mutation": True,
        "human_review_required": True,
    })


class OntologyCandidateConcept(StrictModel):
    label: str
    candidate_type: Literal[
        "role",
        "activity",
        "artifact",
        "system",
        "event_class_candidate",
        "route_candidate",
        "exception_class_candidate",
        "constraint_candidate",
        "metric_candidate",
    ]
    suggested_id: str
    definition: str
    synonyms: list[str] = Field(default_factory=list)
    status: Literal["candidate_only"] = "candidate_only"


class OntologyCandidateRelationship(StrictModel):
    subject: str
    predicate: str
    object: str


class OntologyDeltaCandidate(StrictModel):
    ontology_delta_candidate_id: str
    schema_type: Literal["ontology-delta-candidate"] = "ontology-delta-candidate"
    schema_version: Literal["v1"] = "v1"
    source_workflow_fragment_id: str
    candidate_concepts: list[OntologyCandidateConcept] = Field(default_factory=list)
    candidate_relationships: list[OntologyCandidateRelationship] = Field(default_factory=list)
    promotion_allowed: bool = False
    human_review_required: bool = True


class IntegrityFinding(StrictModel):
    finding_type: str
    severity: Literal["low", "medium", "high"] = "medium"
    summary: str
    source_refs: list[str] = Field(default_factory=list)
    recommended_followup: str


class IntegrityReport(StrictModel):
    integrity_report_id: str
    schema_type: Literal["workflow-integrity-report"] = "workflow-integrity-report"
    schema_version: Literal["v1"] = "v1"
    workflow_fragment_id: str
    source_count: int
    same_job_role_source_count: int
    source_diversity_score: float = Field(ge=0.0, le=1.0)
    contradiction_count: int
    confidence_score: float = Field(ge=0.0, le=1.0)
    findings: list[IntegrityFinding] = Field(default_factory=list)
    recommended_integrity_action: str


class PriorityColoring(StrictModel):
    priority_coloring_id: str
    schema_type: Literal["workflow-priority-coloring"] = "workflow-priority-coloring"
    schema_version: Literal["v1"] = "v1"
    workflow_fragment_id: str
    north_star: Literal["increase_realized_governed_value_per_human_decision_hour"] = "increase_realized_governed_value_per_human_decision_hour"
    scores: dict[str, float]
    priority_score: float = Field(ge=0.0, le=1.0)
    lake_evidence_status: Literal["supported", "missing_or_partial", "missing_manual", "not_checked"]
    likely_lake_gap_reason: str | None = None
    recommended_next_step: Literal[
        "clarify_workflow",
        "instrument_first",
        "prepare_innovation_meeting",
        "pilot_candidate",
        "backlog",
    ]


class MuskAlgorithmReview(StrictModel):
    musk_review_id: str
    schema_type: Literal["musk-algorithm-review"] = "musk-algorithm-review"
    schema_version: Literal["v1"] = "v1"
    workflow_fragment_id: str
    requirement_questions: list[str] = Field(default_factory=list)
    deletion_candidates: list[str] = Field(default_factory=list)
    simplification_candidates: list[str] = Field(default_factory=list)
    acceleration_candidates: list[str] = Field(default_factory=list)
    automation_candidates_after_simplification: list[str] = Field(default_factory=list)
    must_not_automate_yet: list[str] = Field(default_factory=list)
    sequence_rule: str = "question_requirements_delete_simplify_accelerate_automate_last"


class MeetingPrepPacket(StrictModel):
    prep_packet_id: str
    schema_type: Literal["workflow-atlas-meeting-prep-packet"] = "workflow-atlas-meeting-prep-packet"
    schema_version: Literal["v1"] = "v1"
    topic: str
    workflow_fragment_id: str
    diagram_ref: str
    ontology_delta_candidate_id: str
    integrity_report_id: str
    priority_coloring_id: str
    musk_review_id: str
    exception_lake_signal_ref: str
    status: Literal["draft", "ready_for_meeting", "needs_more_intake"]
    open_questions: list[str] = Field(default_factory=list)
    recommended_meeting_decision: str
    candidate_only: bool = True
    no_canonical_mutation: bool = True
