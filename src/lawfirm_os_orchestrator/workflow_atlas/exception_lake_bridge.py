from __future__ import annotations

from lawfirm_os_orchestrator.domain.models import ClassificationResult, SourceClaimRef, SyntheticExceptionInput
from lawfirm_os_orchestrator.workflow_atlas.models import IntegrityReport, PriorityColoring, WorkflowFragment, WorkflowIntakeSession


def build_lake_signal(fragment: WorkflowFragment, integrity: IntegrityReport, priority: PriorityColoring) -> dict:
    return {
        "schema_type": "workflow-atlas-exception-lake-signal",
        "schema_version": "v1",
        "route_id": "route.workflow_escalation.v1",
        "event_class": "workflow_escalation",
        "workflow_fragment_id": fragment.workflow_fragment_id,
        "integrity_report_id": integrity.integrity_report_id,
        "priority_coloring_id": priority.priority_coloring_id,
        "lake_evidence_status": priority.lake_evidence_status,
        "likely_lake_gap_reason": priority.likely_lake_gap_reason,
        "recommended_next_step": priority.recommended_next_step,
        "canonical_mutation_control": {
            "direct_mutation_attempted": False,
            "candidate_only": True,
            "promotion_decision_required_for_canonical_change": True,
        },
    }


def build_synthetic_exception_input(fragment: WorkflowFragment, sessions: list[WorkflowIntakeSession], priority: PriorityColoring) -> SyntheticExceptionInput:
    source_refs = [SourceClaimRef(claim_ref=f"workflow-atlas://{session.intake_session_id}", sha256=session.transcript_hash) for session in sessions[:5]]
    summary = f"Workflow Atlas candidate: {fragment.title}. Recommended next step: {priority.recommended_next_step}."
    return SyntheticExceptionInput(
        input_id=fragment.workflow_fragment_id,
        synthetic=True,
        contains_real_client_data=False,
        contains_real_matter_data=False,
        source_type="workflow_atlas_synthetic_or_redacted_intake",
        route_hint="route.workflow_escalation.v1",
        confidentiality_label="synthetic",
        privilege_label="none",
        source_claim_refs=source_refs,
        payload={
            "summary": summary,
            "workflow_fragment_id": fragment.workflow_fragment_id,
            "systems": fragment.systems,
            "roles": fragment.roles,
            "exception_points": [exc.model_dump() for exc in fragment.exception_points],
            "lake_evidence_status": priority.lake_evidence_status,
            "candidate_only": True,
        },
    )


def workflow_escalation_classification(fragment: WorkflowFragment, priority: PriorityColoring) -> ClassificationResult:
    severity = "high" if priority.priority_score >= 0.65 else "medium"
    return ClassificationResult(
        route_id="route.workflow_escalation.v1",
        event_class="workflow_escalation",
        severity=severity,  # type: ignore[arg-type]
        reason_codes=[
            "workflow_atlas_candidate",
            priority.recommended_next_step,
            priority.lake_evidence_status,
        ],
        supporting_claim_refs=[f"workflow-atlas://{ref}" for ref in fragment.source_intake_ids[:5]],
        confidence=priority.priority_score,
        notes=f"Workflow Atlas evidence candidate for {fragment.title}; no canonical mutation attempted.",
    )
