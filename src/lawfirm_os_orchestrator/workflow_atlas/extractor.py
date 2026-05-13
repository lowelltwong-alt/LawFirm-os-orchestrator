from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.workflow_atlas.models import (
    DecisionPoint,
    ExceptionPoint,
    OntologyCandidateConcept,
    OntologyCandidateRelationship,
    OntologyDeltaCandidate,
    WorkflowFragment,
    WorkflowIntakeSession,
    WorkflowStep,
)

ROLE_TERMS = [
    "attorney", "lawyer", "partner", "relationship partner", "paralegal", "assistant",
    "billing manager", "billing specialist", "billing assistant", "reviewer", "approver",
    "client", "carrier", "adjuster", "portal team", "innovation", "operations",
]

SYSTEM_TERMS = [
    "billblast", "aderant", "billing system", "3e", "elite", "teamconnect", "legal tracker",
    "counsel link", "tymetrix", "datatrac", "carrier portal", "insurance portal", "portal",
    "email", "outlook", "teams", "spreadsheet", "excel", "sharepoint", "onedrive",
    "word", "dms", "imanage", "netdocuments", "planner", "power automate", "purview",
]

ARTIFACT_TERMS = [
    "invoice", "bill", "pre-bill", "prebill", "proforma", "guideline", "checklist",
    "email", "time entry", "narrative", "receipt", "rejection", "budget", "matter",
    "document", "report", "submission", "approval", "spreadsheet", "status", "queue",
]

METRIC_TERMS = {
    "realization": ["realization", "write-down", "write down", "denial", "deduction"],
    "labor_drag": ["manual", "rework", "rewrite", "redo", "copy", "paste", "retype"],
    "cycle_time": ["delay", "wait", "stuck", "queue", "late", "turnaround"],
    "billing_integrity": ["billing", "invoice", "guideline", "compliance"],
    "client_carrier_pressure": ["client", "carrier", "ocg", "portal", "guideline"],
}

ACTION_RE = re.compile(r"\b(receive|review|check|update|submit|reject|approve|rewrite|fix|upload|send|route|export|log|compare|enter|open|search|download|copy|paste|reconcile)\b", re.I)


def _norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "unknown"


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _first_header(text: str, key: str) -> str | None:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*[:=]\s*(.+?)\s*$", re.I | re.M)
    match = pattern.search(text)
    return match.group(1).strip() if match else None


def _sentences(text: str) -> list[str]:
    rough = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [s.strip(" -\t") for s in rough if len(s.strip()) >= 12]


def _terms_found(text: str, terms: list[str]) -> list[str]:
    low = text.lower()
    found = []
    for term in terms:
        if term in low:
            found.append(term)
    return sorted(set(found))


def read_intake_file(path: Path, topic: str) -> WorkflowIntakeSession:
    raw = path.read_text(encoding="utf-8")
    source_type = "manual_transcript"
    speaker_role = _first_header(raw, "speaker_role") or _first_header(raw, "role") or path.stem.replace("_", " ")
    speaker_job_key = _first_header(raw, "speaker_job_key") or _norm(speaker_role)
    if path.suffix.lower() == ".json":
        data = json.loads(raw)
        if "transcript" in data:
            raw = str(data["transcript"])
        source_type = data.get("source_type", source_type)
        speaker_role = data.get("speaker_role", speaker_role)
        speaker_job_key = data.get("speaker_job_key", speaker_job_key)
    return WorkflowIntakeSession(
        intake_session_id=new_id("intake"),
        topic=topic,
        source_type=source_type,  # type: ignore[arg-type]
        speaker_role=speaker_role,
        speaker_job_key=speaker_job_key,
        transcript_ref=str(path),
        transcript_hash=_hash_text(raw),
        transcript_excerpt=raw[:1200],
    )


def extract_workflow_fragment(topic: str, sessions: list[WorkflowIntakeSession]) -> WorkflowFragment:
    combined = "\n".join(s.transcript_excerpt for s in sessions)
    sentences = _sentences(combined)
    roles = sorted(set(_terms_found(combined, ROLE_TERMS) + [s.speaker_role for s in sessions]))
    systems = _terms_found(combined, SYSTEM_TERMS)
    artifacts = _terms_found(combined, ARTIFACT_TERMS)
    metrics = [metric for metric, terms in METRIC_TERMS.items() if any(t in combined.lower() for t in terms)]
    trigger = next((s for s in sentences if any(k in s.lower() for k in ["starts", "begins", "when", "arrives", "first"])), "Workflow reported through intake")

    steps: list[WorkflowStep] = []
    for sentence in sentences:
        if not ACTION_RE.search(sentence):
            continue
        actor = next((r for r in roles if r.lower() in sentence.lower()), sessions[0].speaker_role)
        system = next((sys for sys in systems if sys in sentence.lower()), None)
        inputs = [a for a in artifacts if a in sentence.lower()][:4]
        exceptions = []
        if any(k in sentence.lower() for k in ["reject", "rework", "delay", "missing", "stale", "manual", "write-down", "write down", "denial"]):
            exceptions.append("possible_rework_or_failure_point")
        steps.append(WorkflowStep(
            step_id=f"S{len(steps)+1}",
            actor_role=actor,
            activity=sentence[:180],
            system=system,
            input_artifacts=inputs,
            output_artifacts=[] if system is None else [f"{_norm(system)}_status_or_record"],
            evidence_refs=[f"workflow-intake:{s.intake_session_id}" for s in sessions[:2]],
            exceptions=exceptions,
            confidence=0.55 if system else 0.42,
        ))
        if len(steps) >= 12:
            break

    if not steps:
        steps = [WorkflowStep(step_id="S1", actor_role=sessions[0].speaker_role, activity="Map the described workflow from the intake story", confidence=0.25)]

    decision_points: list[DecisionPoint] = []
    for sentence in sentences:
        if " if " in f" {sentence.lower()} " or sentence.lower().startswith("if "):
            decision_points.append(DecisionPoint(decision_id=f"D{len(decision_points)+1}", question=sentence[:160], paths=["normal_path", "exception_path"]))
    if not decision_points and any(step.exceptions for step in steps):
        decision_points.append(DecisionPoint(decision_id="D1", question="Does the workflow follow the normal path or create rework?", paths=["normal_path", "rework_exception_path"]))

    exception_points: list[ExceptionPoint] = []
    low = combined.lower()
    exception_map = {
        "manual_rework": ["manual", "rework", "rewrite", "redo"],
        "portal_rejection": ["portal", "reject"],
        "stale_guidance": ["stale", "guideline", "checklist"],
        "billing_delay_or_write_down": ["write-down", "write down", "delay", "denial", "deduction"],
    }
    for label, words in exception_map.items():
        if all(word in low for word in words[:2]) or any(word in low for word in words):
            exception_points.append(ExceptionPoint(
                exception_label=label.replace("_", " ").title(),
                candidate_exception_class=label,
                impacts=[m for m in metrics] or ["review_rework"],
            ))

    handoffs = []
    for i in range(1, len(steps)):
        if steps[i - 1].actor_role != steps[i].actor_role:
            handoffs.append(f"{steps[i-1].actor_role} -> {steps[i].actor_role}")

    open_questions = []
    if len(sessions) < 2:
        open_questions.append("Interview at least one more source before treating this workflow as stable.")
    if not systems:
        open_questions.append("Which systems, portals, reports, queues, or tools are used at each step?")
    if not exception_points:
        open_questions.append("Where does this workflow fail, slow down, or require manual rework?")
    if "billblast" in combined.lower():
        open_questions.append("For BillBlast, identify the module, queue, status, rejection code, and evidence export used in this workflow.")
    if "portal" in combined.lower():
        open_questions.append("For each insurance portal, identify required fields, validation errors, confirmation receipts, and appeal/rejection path.")

    confidence = {
        "workflow_order": min(0.85, 0.25 + len(steps) * 0.05 + len(sessions) * 0.08),
        "actor_mapping": min(0.85, 0.35 + len(roles) * 0.04),
        "system_mapping": min(0.85, 0.25 + len(systems) * 0.08),
        "exception_mapping": min(0.85, 0.25 + len(exception_points) * 0.12),
    }

    return WorkflowFragment(
        workflow_fragment_id=new_id("wf_frag"),
        title=topic,
        source_intake_ids=[s.intake_session_id for s in sessions],
        trigger=trigger[:240],
        roles=roles,
        systems=systems,
        artifacts=artifacts,
        steps=steps,
        decision_points=decision_points,
        exception_points=exception_points,
        handoffs=handoffs,
        metrics_affected=metrics,
        open_questions=open_questions,
        confidence=confidence,
    )


def build_ontology_delta(fragment: WorkflowFragment) -> OntologyDeltaCandidate:
    concepts: list[OntologyCandidateConcept] = []
    for role in fragment.roles:
        concepts.append(OntologyCandidateConcept(label=role, candidate_type="role", suggested_id=f"role.{_norm(role)}", definition=f"Role mentioned in workflow fragment {fragment.workflow_fragment_id}."))
    for system in fragment.systems:
        concepts.append(OntologyCandidateConcept(label=system, candidate_type="system", suggested_id=f"system.{_norm(system)}", definition=f"Technology system or portal used in workflow fragment {fragment.workflow_fragment_id}."))
    for artifact in fragment.artifacts:
        concepts.append(OntologyCandidateConcept(label=artifact, candidate_type="artifact", suggested_id=f"artifact.{_norm(artifact)}", definition=f"Artifact mentioned in workflow fragment {fragment.workflow_fragment_id}."))
    for exc in fragment.exception_points:
        concepts.append(OntologyCandidateConcept(label=exc.exception_label, candidate_type="exception_class_candidate", suggested_id=f"exception.{_norm(exc.candidate_exception_class)}", definition="Candidate exception class discovered from workflow intake; candidate-only until semantic review."))

    relationships = []
    for step in fragment.steps:
        if step.system:
            relationships.append(OntologyCandidateRelationship(subject=f"role.{_norm(step.actor_role)}", predicate="uses_system", object=f"system.{_norm(step.system)}"))
    for metric in fragment.metrics_affected:
        relationships.append(OntologyCandidateRelationship(subject=f"workflow.{_norm(fragment.title)}", predicate="affects_metric", object=f"metric.{_norm(metric)}"))

    return OntologyDeltaCandidate(
        ontology_delta_candidate_id=new_id("ont_cand"),
        source_workflow_fragment_id=fragment.workflow_fragment_id,
        candidate_concepts=concepts[:40],
        candidate_relationships=relationships[:40],
    )
