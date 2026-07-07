from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.intake.lake_admission_review import (
    prepare_intake_lake_admission_review_packet,
    write_intake_lake_admission_review_artifacts,
)
from lawfirm_os_orchestrator.intake.owner_review import (
    prepare_intake_owner_review_packet,
    write_intake_owner_review_artifacts,
)
from lawfirm_os_orchestrator.ledger.writer import JsonlLedgerWriter
from lawfirm_os_orchestrator.util.hashing import canonical_json
from lawfirm_os_orchestrator.util.json_io import write_json
from lawfirm_os_orchestrator.util.time import utc_now


SCHEMA_VERSION = "intake_vertical_slice_demo.v0_1"
LOCAL_WORKFLOW_LABEL = "orchestrator.local.intake_no_write_vertical_slice_demo"

REQUIRED_SIBLING_SURFACES: tuple[tuple[str, str, str], ...] = (
    (
        "LawFirm-os-semantic-substrate",
        "control_plane",
        "registry/governance-dependency-map.json",
    ),
    (
        "LawFirm-os-semantic-substrate",
        "control_plane",
        "registry/lawfirm-os-repo-registry.json",
    ),
    (
        "LawFirm-os-intake",
        "vertical_workflow_composition",
        "BUILD_VERIFICATION.md",
    ),
    (
        "LawFirm-os-intake",
        "vertical_workflow_composition",
        "contracts.lock.json",
    ),
    (
        "LawFirm-os-legal-knowledge-runtime",
        "legal_knowledge_runtime",
        "AI_WORK_START_HERE.md",
    ),
    (
        "LawFirm-os-legal-knowledge-runtime",
        "legal_knowledge_runtime",
        "src/lawfirm_os_legal_knowledge/cli.py",
    ),
    (
        "LawFirm-os-exceptions-lake-runtime",
        "evidence_plane",
        "examples/legal_document_integrity_check_event.json",
    ),
    (
        "LawFirm-os-skills-registry",
        "skills_registry",
        "registry/proposed-draft-skill-index.json",
    ),
)

NO_WRITE_CONTROLS = {
    "synthetic_only": True,
    "external_write_authorized": False,
    "semantic_substrate_write_authorized": False,
    "exception_lake_write_authorized": False,
    "sqlite_write_authorized": False,
    "raw_payload_storage_authorized": False,
    "client_or_carrier_submission_authorized": False,
    "matter_opening_authorized": False,
    "conflict_clearance_authorized": False,
    "canonical_route_or_event_creation_authorized": False,
    "model_call_authorized": False,
}


def _rel(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def _surface_checks(workspace: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for repo, plane, rel in REQUIRED_SIBLING_SURFACES:
        path = workspace / repo / rel
        checks.append(
            {
                "repo": repo,
                "plane": plane,
                "path": rel,
                "exists": path.exists(),
                "status": "present" if path.exists() else "missing",
            }
        )
    return checks


def _report_hash(report: dict[str, Any]) -> str:
    clean = {key: value for key, value in report.items() if key != "report_hash"}
    return hashlib.sha256(canonical_json(clean)).hexdigest()


def _markdown(report: dict[str, Any]) -> str:
    checks = "\n".join(
        f"- `{item['repo']}` `{item['path']}`: `{item['status']}`"
        for item in report["sibling_surface_checks"]
    )
    review_items = "\n".join(
        f"- [{item['status']}] {item['label']}: {item['required_decision']}"
        for item in report["attorney_review_packet"]["checklist"]
    )
    prohibited = "\n".join(
        f"- `{action}`" for action in report["attorney_review_packet"]["prohibited_actions"]
    )
    blockers = "\n".join(f"- `{blocker}`" for blocker in report["blockers"])
    return (
        "# Intake No-Write Vertical Slice Demo\n\n"
        f"Demo: `{report['demo_id']}`\n\n"
        f"Status: `{report['status']}`\n\n"
        "## No-Write Controls\n\n"
        "- synthetic-only\n"
        "- no client/carrier submission\n"
        "- no matter opening or conflict clearance\n"
        "- no Semantic Substrate write\n"
        "- no Exception Lake/SQLite write\n"
        "- no canonical route or event-class creation\n"
        "- no model call\n\n"
        "## Sibling Surface Checks\n\n"
        f"{checks}\n\n"
        "## Generated Review Artifacts\n\n"
        f"- Owner review packet: `{report['owner_review_packet_ref']}`\n"
        f"- Lake admission review packet: `{report['lake_admission_review_packet_ref']}`\n\n"
        "## Attorney Review Checklist\n\n"
        f"{review_items}\n\n"
        "## Prohibited Actions\n\n"
        f"{prohibited}\n\n"
        "## Blockers\n\n"
        f"{blockers}\n"
    )


def build_intake_vertical_slice_demo(
    *,
    request: dict[str, Any],
    workspace: Path,
    owner_packet_ref: str,
    lake_packet_ref: str,
    generated_at: str | None = None,
) -> dict[str, Any]:
    surface_checks = _surface_checks(workspace)
    owner_packet = prepare_intake_owner_review_packet(request)
    lake_packet = prepare_intake_lake_admission_review_packet(owner_packet)
    missing_surfaces = [
        f"{item['repo']}:{item['path']}"
        for item in surface_checks
        if item["status"] != "present"
    ]
    blockers = [
        *(f"owner:{blocker}" for blocker in owner_packet.get("blockers", [])),
        *(f"lake:{blocker}" for blocker in lake_packet.get("blockers", [])),
        *(f"sibling_surface_missing:{surface}" for surface in missing_surfaces),
        "attorney_review:required_before_reliance",
        "owner_decision:required_before_any_real_data_or_production_use",
    ]
    status = (
        "blocked_pending_attorney_and_owner_review"
        if blockers
        else "proposed_for_attorney_review"
    )
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "demo_id": "intake_vertical_slice_"
        + hashlib.sha256(canonical_json({"request": request})).hexdigest()[:16],
        "generated_at": generated_at or utc_now(),
        "source_repo": "LawFirm-os-orchestrator",
        "source_vertical_repo": "LawFirm-os-intake",
        "workflow_label": LOCAL_WORKFLOW_LABEL,
        "status": status,
        "synthetic": True,
        "non_authoritative": True,
        "no_write_controls": dict(NO_WRITE_CONTROLS),
        "sibling_surface_checks": surface_checks,
        "owner_review_packet_ref": owner_packet_ref,
        "owner_review_packet_status": owner_packet["status"],
        "owner_review_packet_hash": owner_packet["packet_hash"],
        "lake_admission_review_packet_ref": lake_packet_ref,
        "lake_admission_review_packet_status": lake_packet["status"],
        "lake_admission_review_packet_hash": lake_packet["packet_hash"],
        "attorney_review_packet": {
            "status": "required",
            "reliance_posture": "not_reliable_for_client_or_court_use_until_attorney_owner_gates_pass",
            "review_surfaces": [
                owner_packet_ref,
                lake_packet_ref,
                "intake_vertical_slice_demo_report.md",
            ],
            "checklist": [
                {
                    "item_id": "review_source_binding",
                    "label": "Source binding",
                    "status": "required",
                    "required_decision": "Attorney verifies source refs, hashes, and missing-source blockers before relying on facts.",
                },
                {
                    "item_id": "review_matter_posture",
                    "label": "Matter posture",
                    "status": "required",
                    "required_decision": "Attorney confirms matter family, representation posture, and principal party roles.",
                },
                {
                    "item_id": "review_conflicts",
                    "label": "Conflicts",
                    "status": "required",
                    "required_decision": "Conflicts owner performs clearance; this demo only prepares seeds and blockers.",
                },
                {
                    "item_id": "review_budget",
                    "label": "Budget proposal",
                    "status": "required",
                    "required_decision": "Pricing or attorney reviewer approves, revises, or rejects the budget proposal before any external use.",
                },
                {
                    "item_id": "review_lake_admission",
                    "label": "Lake admission",
                    "status": "required",
                    "required_decision": "Exception Lake owner accepts or rejects candidate record families before any Lake/SQLite write.",
                },
                {
                    "item_id": "review_client_use",
                    "label": "Client or carrier use",
                    "status": "blocked",
                    "required_decision": "No client, carrier, court, or production use is authorized by this demo.",
                },
            ],
            "must_confirm": [
                "matter_family",
                "representation_posture",
                "principal_party_roles",
                "conflicts_clearance",
                "engagement_authorization",
                "budget_review",
                "exception_lake_admission",
            ],
            "prohibited_actions": [
                "client_or_carrier_submission",
                "court_or_filing_use",
                "conflict_clearance",
                "matter_opening",
                "exception_lake_or_sqlite_write",
                "semantic_substrate_write",
                "canonical_route_or_event_creation",
            ],
        },
        "blockers": sorted(set(blockers)),
    }
    report["report_hash"] = _report_hash(report)
    return report


def write_intake_vertical_slice_demo_artifacts(
    *,
    request: dict[str, Any],
    workspace: Path,
    out_dir: Path,
    ledger_dir: Path,
) -> dict[str, Any]:
    owner_packet = prepare_intake_owner_review_packet(request)
    owner_summary = write_intake_owner_review_artifacts(
        packet=owner_packet,
        out_dir=out_dir / "owner_review",
        ledger_dir=ledger_dir,
    )
    lake_packet = prepare_intake_lake_admission_review_packet(owner_packet)
    lake_summary = write_intake_lake_admission_review_artifacts(
        packet=lake_packet,
        out_dir=out_dir / "lake_admission_review",
        ledger_dir=ledger_dir,
    )
    report = build_intake_vertical_slice_demo(
        request=request,
        workspace=workspace,
        owner_packet_ref=owner_summary["packet_path"],
        lake_packet_ref=lake_summary["packet_path"],
    )
    report_dir = out_dir / report["demo_id"]
    report_path = report_dir / "intake_vertical_slice_demo_report.json"
    markdown_path = report_dir / "intake_vertical_slice_demo_report.md"
    write_json(report_path, report)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_markdown(report), encoding="utf-8")

    ledger_path = ledger_dir / "intake_vertical_slice_demo.jsonl"
    JsonlLedgerWriter(ledger_path).append(
        {
            "ledger_version": "1",
            "command_name": "intake run-vertical-slice-demo",
            "demo_id": report["demo_id"],
            "status": report["status"],
            "synthetic": True,
            "non_authoritative": True,
            "external_write_authorized": False,
            "exception_lake_write_authorized": False,
            "timestamp": report["generated_at"],
            "report_hash": report["report_hash"],
        }
    )

    summary = {
        "status": report["status"],
        "demo_id": report["demo_id"],
        "report_hash": report["report_hash"],
        "report_path": str(report_path),
        "markdown_path": str(markdown_path),
        "owner_packet_path": owner_summary["packet_path"],
        "lake_packet_path": lake_summary["packet_path"],
        "ledger_path": str(ledger_path),
        "sibling_surface_status": "passed"
        if all(item["exists"] for item in report["sibling_surface_checks"])
        else "blocked",
        "external_write_authorized": False,
        "exception_lake_write_authorized": False,
        "not_authorized_for_client_submission": True,
        "blocker_count": len(report["blockers"]),
    }
    write_json(report_dir / "stdout_summary.json", summary)
    return summary
