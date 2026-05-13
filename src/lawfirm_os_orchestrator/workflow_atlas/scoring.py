from __future__ import annotations

from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.workflow_atlas.models import IntegrityReport, PriorityColoring, WorkflowFragment


def _has_any(text: str, terms: list[str]) -> bool:
    low = text.lower()
    return any(term in low for term in terms)


def _clip(value: float) -> float:
    return round(max(0.0, min(1.0, value)), 3)


def score_priority(fragment: WorkflowFragment, integrity: IntegrityReport) -> PriorityColoring:
    text = " ".join([
        fragment.title,
        fragment.trigger,
        " ".join(fragment.systems),
        " ".join(fragment.artifacts),
        " ".join(step.activity for step in fragment.steps),
        " ".join(exc.candidate_exception_class for exc in fragment.exception_points),
    ]).lower()

    realization = 0.8 if _has_any(text, ["realization", "write-down", "write down", "denial", "deduction", "invoice", "billing"]) else 0.25
    labor_drag = 0.75 if _has_any(text, ["manual", "rework", "rewrite", "redo", "copy", "paste", "retype"]) else 0.3
    recurrence = 0.7 if _has_any(text, ["weekly", "daily", "often", "repeated", "every", "usually"]) else 0.4
    cycle_time = 0.7 if _has_any(text, ["delay", "wait", "stuck", "queue", "late"]) else 0.3
    client_carrier = 0.8 if _has_any(text, ["client", "carrier", "ocg", "portal", "guideline"]) else 0.3
    risk_reduction = 0.65 if _has_any(text, ["deadline", "compliance", "privilege", "guideline", "approval", "audit"]) else 0.25
    reusability = 0.75 if len(fragment.systems) >= 2 or len(fragment.roles) >= 3 else 0.4
    evidence_readiness = integrity.confidence_score
    governance_load = 0.65 if _has_any(text, ["approve", "submit", "send", "client", "carrier", "portal"]) else 0.35
    effort = 0.55 if len(fragment.systems) >= 3 else 0.35
    dependency = 0.55 if _has_any(text, ["portal", "billblast", "aderant", "dms", "sharepoint"]) else 0.3

    weighted_value = (
        0.18 * realization + 0.16 * labor_drag + 0.12 * recurrence + 0.11 * cycle_time +
        0.12 * client_carrier + 0.09 * risk_reduction + 0.08 * reusability + 0.14 * evidence_readiness
    )
    burden = 1.0 + (0.35 * effort) + (0.35 * governance_load) + (0.25 * dependency)
    priority = _clip(weighted_value / burden * 1.65)

    manual_systems = {"email", "spreadsheet", "excel", "teams"}
    if any(sys in manual_systems for sys in fragment.systems):
        lake_status = "missing_or_partial"
        reason = "manual_process_or_microsoft_workflow_outside_current_exception_lake"
    elif integrity.confidence_score < 0.5:
        lake_status = "not_checked"
        reason = "insufficient_intake_confidence"
    else:
        lake_status = "missing_or_partial"
        reason = "needs_exception_lake_lookup_or_instrumentation"

    if integrity.contradiction_count > 0 or integrity.confidence_score < 0.45:
        next_step = "clarify_workflow"
    elif lake_status in {"missing_or_partial", "missing_manual"} and priority >= 0.45:
        next_step = "instrument_first"
    elif priority >= 0.65:
        next_step = "pilot_candidate"
    elif priority >= 0.45:
        next_step = "prepare_innovation_meeting"
    else:
        next_step = "backlog"

    return PriorityColoring(
        priority_coloring_id=new_id("priority"),
        workflow_fragment_id=fragment.workflow_fragment_id,
        scores={
            "realization_effect": _clip(realization),
            "labor_drag": _clip(labor_drag),
            "recurrence": _clip(recurrence),
            "cycle_time_effect": _clip(cycle_time),
            "client_carrier_pressure": _clip(client_carrier),
            "risk_reduction": _clip(risk_reduction),
            "reusability": _clip(reusability),
            "evidence_confidence": _clip(evidence_readiness),
            "effort": _clip(effort),
            "governance_load": _clip(governance_load),
            "dependency": _clip(dependency),
        },
        priority_score=priority,
        lake_evidence_status=lake_status,  # type: ignore[arg-type]
        likely_lake_gap_reason=reason,
        recommended_next_step=next_step,  # type: ignore[arg-type]
    )
