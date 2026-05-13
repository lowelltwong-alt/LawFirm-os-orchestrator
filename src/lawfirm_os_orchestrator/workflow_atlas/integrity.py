from __future__ import annotations

from collections import Counter, defaultdict

from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.workflow_atlas.models import IntegrityFinding, IntegrityReport, WorkflowFragment, WorkflowIntakeSession

NEGATION_PATTERNS = ["does not", "don't", "do not", "never", "not ", "no "]


def _contains_negation_about(text: str, term: str) -> bool:
    low = text.lower()
    if term.lower() not in low:
        return False
    idx = low.find(term.lower())
    window = low[max(0, idx - 40): idx + len(term) + 40]
    return any(pattern in window for pattern in NEGATION_PATTERNS)


def build_integrity_report(sessions: list[WorkflowIntakeSession], fragment: WorkflowFragment) -> IntegrityReport:
    findings: list[IntegrityFinding] = []
    job_counts = Counter((s.speaker_job_key or s.speaker_role).lower() for s in sessions)
    same_job_role_source_count = max(job_counts.values()) if job_counts else 0
    source_diversity_score = min(1.0, len(job_counts) / 4)

    if len(sessions) < 2:
        findings.append(IntegrityFinding(
            finding_type="single_source_risk",
            severity="high",
            summary="Only one intake source contributed to the workflow map.",
            source_refs=[sessions[0].intake_session_id] if sessions else [],
            recommended_followup="Run at least one same-job intake and one downstream-role intake before meeting.",
        ))
    if same_job_role_source_count < 2:
        findings.append(IntegrityFinding(
            finding_type="same_job_sample_missing",
            severity="medium",
            summary="No role has two independent intakes yet; same-job comparison is weak.",
            recommended_followup="Have at least two people with the same job role run the same short intake.",
        ))

    contradiction_count = 0
    for term in fragment.systems + fragment.artifacts:
        affirmers = []
        negaters = []
        for session in sessions:
            text = session.transcript_excerpt.lower()
            if term.lower() in text:
                if _contains_negation_about(text, term):
                    negaters.append(session.intake_session_id)
                else:
                    affirmers.append(session.intake_session_id)
        if affirmers and negaters:
            contradiction_count += 1
            findings.append(IntegrityFinding(
                finding_type="cross_source_contradiction",
                severity="high",
                summary=f"Some sources affirm `{term}` while others negate or dispute it.",
                source_refs=affirmers + negaters,
                recommended_followup=f"Ask the group to resolve whether `{term}` is actually part of the workflow, a variant, or a terminology issue.",
            ))

    same_job_systems: dict[str, list[set[str]]] = defaultdict(list)
    for session in sessions:
        key = (session.speaker_job_key or session.speaker_role).lower()
        text = session.transcript_excerpt.lower()
        same_job_systems[key].append({system for system in fragment.systems if system in text})
    for key, system_sets in same_job_systems.items():
        if len(system_sets) >= 2:
            union = set().union(*system_sets)
            intersection = set.intersection(*system_sets) if system_sets else set()
            if union and len(intersection) / len(union) < 0.45:
                findings.append(IntegrityFinding(
                    finding_type="same_job_variant_or_bad_data",
                    severity="medium",
                    summary=f"People with job key `{key}` described materially different system involvement.",
                    recommended_followup="Ask whether this is a real variant, memory gap, training gap, or bad intake data.",
                ))

    if not fragment.systems:
        findings.append(IntegrityFinding(
            finding_type="low_technology_detail",
            severity="high",
            summary="The workflow map has little or no technology detail.",
            recommended_followup="Run the tech-workflow-discoverer skill for each vague system step.",
        ))
    if any(sys in fragment.systems for sys in ["email", "spreadsheet", "excel", "teams"]) and not any("exception lake" in s.transcript_excerpt.lower() for s in sessions):
        findings.append(IntegrityFinding(
            finding_type="likely_manual_process_outside_exception_lake",
            severity="medium",
            summary="The described pain appears to live in manual Microsoft/email/spreadsheet work rather than current Exception Lake instrumentation.",
            recommended_followup="Create a manual-shadow-exception capture for 30 days before automation.",
        ))

    confidence = 0.25 + min(0.25, len(sessions) * 0.07) + source_diversity_score * 0.2 + min(0.2, len(fragment.steps) * 0.02)
    confidence -= min(0.3, contradiction_count * 0.08)
    confidence = max(0.05, min(1.0, round(confidence, 3)))
    if contradiction_count > 0:
        action = "resolve_contradictions_before_meeting"
    elif confidence < 0.55:
        action = "collect_more_intakes"
    else:
        action = "ready_for_visual_correction"

    return IntegrityReport(
        integrity_report_id=new_id("integrity"),
        workflow_fragment_id=fragment.workflow_fragment_id,
        source_count=len(sessions),
        same_job_role_source_count=same_job_role_source_count,
        source_diversity_score=round(source_diversity_score, 3),
        contradiction_count=contradiction_count,
        confidence_score=confidence,
        findings=findings,
        recommended_integrity_action=action,
    )
