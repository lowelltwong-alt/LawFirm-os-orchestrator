from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.json_io import write_json
from lawfirm_os_orchestrator.workflow_atlas.models import (
    IntegrityReport,
    MeetingPrepPacket,
    MuskAlgorithmReview,
    OntologyDeltaCandidate,
    PriorityColoring,
    WorkflowFragment,
)


def _bullets(items: list[str]) -> str:
    if not items:
        return "- None captured yet."
    return "\n".join(f"- {item}" for item in items)


def build_meeting_prep_packet(
    *,
    topic: str,
    fragment: WorkflowFragment,
    diagram_relpath: str,
    ontology: OntologyDeltaCandidate,
    integrity: IntegrityReport,
    priority: PriorityColoring,
    musk: MuskAlgorithmReview,
    lake_signal_ref: str,
) -> MeetingPrepPacket:
    status = "ready_for_meeting" if integrity.confidence_score >= 0.55 and integrity.contradiction_count == 0 else "needs_more_intake"
    decision = priority.recommended_next_step
    return MeetingPrepPacket(
        prep_packet_id=new_id("prep"),
        topic=topic,
        workflow_fragment_id=fragment.workflow_fragment_id,
        diagram_ref=diagram_relpath,
        ontology_delta_candidate_id=ontology.ontology_delta_candidate_id,
        integrity_report_id=integrity.integrity_report_id,
        priority_coloring_id=priority.priority_coloring_id,
        musk_review_id=musk.musk_review_id,
        exception_lake_signal_ref=lake_signal_ref,
        status=status,  # type: ignore[arg-type]
        open_questions=fragment.open_questions,
        recommended_meeting_decision=decision,
    )


def render_prep_markdown(
    *,
    packet: MeetingPrepPacket,
    fragment: WorkflowFragment,
    diagram: str,
    integrity: IntegrityReport,
    priority: PriorityColoring,
    musk: MuskAlgorithmReview,
    lake_signal: dict[str, Any],
) -> str:
    lake_signal_json = json.dumps(lake_signal, indent=2, sort_keys=False)
    return f"""# Workflow Atlas Meeting Prep Packet

## Topic

{packet.topic}

## Candidate-only boundary

- Candidate only: `{packet.candidate_only}`
- No canonical mutation: `{packet.no_canonical_mutation}`
- Human review required before ontology or digital-twin promotion.

## Draft workflow diagram

```mermaid
{diagram.strip()}
```

## Workflow summary

- Workflow fragment: `{fragment.workflow_fragment_id}`
- Trigger: {fragment.trigger}
- Roles: {', '.join(fragment.roles) if fragment.roles else 'unknown'}
- Systems: {', '.join(fragment.systems) if fragment.systems else 'unknown'}
- Artifacts: {', '.join(fragment.artifacts) if fragment.artifacts else 'unknown'}
- Metrics affected: {', '.join(fragment.metrics_affected) if fragment.metrics_affected else 'unknown'}

## Integrity / bad-data detector

- Integrity confidence: `{integrity.confidence_score}`
- Source count: `{integrity.source_count}`
- Same-job role source count: `{integrity.same_job_role_source_count}`
- Contradiction count: `{integrity.contradiction_count}`
- Recommended integrity action: `{integrity.recommended_integrity_action}`

### Integrity findings

{_bullets([f"{f.severity}: {f.summary} - {f.recommended_followup}" for f in integrity.findings])}

## Priority coloring

- North star: `{priority.north_star}`
- Priority score: `{priority.priority_score}`
- Lake evidence status: `{priority.lake_evidence_status}`
- Likely lake gap reason: `{priority.likely_lake_gap_reason}`
- Recommended next step: `{priority.recommended_next_step}`

### Score inputs

{_bullets([f"{k}: {v}" for k, v in priority.scores.items()])}

## Musk Algorithm Review

### 1. Question requirements

{_bullets(musk.requirement_questions)}

### 2. Delete before optimizing

{_bullets(musk.deletion_candidates)}

### 3. Simplify

{_bullets(musk.simplification_candidates)}

### 4. Accelerate

{_bullets(musk.acceleration_candidates)}

### 5. Automate last

{_bullets(musk.automation_candidates_after_simplification)}

### Must not automate yet

{_bullets(musk.must_not_automate_yet)}

## Exception Lake bridge signal

```json
{lake_signal_json}
```

## Open questions for the innovation meeting

{_bullets(packet.open_questions)}

## Meeting decision options

- `clarify_workflow`
- `instrument_first`
- `prepare_innovation_meeting`
- `pilot_candidate`
- `backlog`
"""


def write_outputs(
    *,
    out_dir: Path,
    fragment: WorkflowFragment,
    diagram: str,
    ontology: OntologyDeltaCandidate,
    integrity: IntegrityReport,
    priority: PriorityColoring,
    musk: MuskAlgorithmReview,
    lake_signal: dict[str, Any],
    lake_receipt: dict[str, Any],
    packet: MeetingPrepPacket,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    write_json(out_dir / "workflow_fragment.json", fragment.model_dump())
    (out_dir / "workflow_diagram.mmd").write_text(diagram, encoding="utf-8")
    write_json(out_dir / "ontology_delta_candidate.json", ontology.model_dump())
    write_json(out_dir / "integrity_report.json", integrity.model_dump())
    write_json(out_dir / "priority_coloring.json", priority.model_dump())
    write_json(out_dir / "musk_algorithm_review.json", musk.model_dump())
    write_json(out_dir / "exception_lake_signal.json", lake_signal)
    write_json(out_dir / "lake_handoff_receipt.json", lake_receipt)
    write_json(out_dir / "meeting_prep_packet.json", packet.model_dump())
    md = render_prep_markdown(packet=packet, fragment=fragment, diagram=diagram, integrity=integrity, priority=priority, musk=musk, lake_signal=lake_signal)
    (out_dir / "meeting_prep_packet.md").write_text(md, encoding="utf-8")
