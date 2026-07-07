#!/usr/bin/env python3
"""Validate an intake no-write vertical-slice demo report."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_SCHEMA_VERSION = "intake_vertical_slice_demo.v0_1"
REQUIRED_STATUS = "blocked_pending_attorney_and_owner_review"
REQUIRED_REPOS = {
    "LawFirm-os-semantic-substrate",
    "LawFirm-os-intake",
    "LawFirm-os-legal-knowledge-runtime",
    "LawFirm-os-exceptions-lake-runtime",
    "LawFirm-os-skills-registry",
}
REQUIRED_REVIEW_ITEMS = {
    "review_source_binding",
    "review_matter_posture",
    "review_conflicts",
    "review_budget",
    "review_lake_admission",
    "review_client_use",
}
FALSE_NO_WRITE_FLAGS = {
    "external_write_authorized",
    "semantic_substrate_write_authorized",
    "exception_lake_write_authorized",
    "sqlite_write_authorized",
    "raw_payload_storage_authorized",
    "client_or_carrier_submission_authorized",
    "matter_opening_authorized",
    "conflict_clearance_authorized",
    "canonical_route_or_event_creation_authorized",
    "model_call_authorized",
}
PROHIBITED_ACTIONS = {
    "client_or_carrier_submission",
    "court_or_filing_use",
    "conflict_clearance",
    "matter_opening",
    "exception_lake_or_sqlite_write",
    "semantic_substrate_write",
    "canonical_route_or_event_creation",
}


class VerticalSliceValidationError(ValueError):
    """Raised when a vertical-slice demo report is unsafe or incomplete."""


def _read_report(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerticalSliceValidationError(f"could not read report: {exc}") from exc
    if not isinstance(payload, dict):
        raise VerticalSliceValidationError("report must be a JSON object")
    return payload


def validate_report(report: dict[str, Any]) -> None:
    if report.get("schema_version") != REQUIRED_SCHEMA_VERSION:
        raise VerticalSliceValidationError("unexpected schema_version")
    if report.get("status") != REQUIRED_STATUS:
        raise VerticalSliceValidationError("report must remain blocked pending attorney and owner review")
    if report.get("synthetic") is not True or report.get("non_authoritative") is not True:
        raise VerticalSliceValidationError("report must be synthetic and non-authoritative")

    controls = report.get("no_write_controls")
    if not isinstance(controls, dict):
        raise VerticalSliceValidationError("no_write_controls must be an object")
    if controls.get("synthetic_only") is not True:
        raise VerticalSliceValidationError("synthetic_only control must be true")
    for flag in FALSE_NO_WRITE_FLAGS:
        if controls.get(flag) is not False:
            raise VerticalSliceValidationError(f"no_write_controls.{flag} must be false")

    checks = report.get("sibling_surface_checks")
    if not isinstance(checks, list) or not checks:
        raise VerticalSliceValidationError("sibling_surface_checks must be non-empty")
    repos = {item.get("repo") for item in checks if isinstance(item, dict)}
    missing_repos = sorted(REQUIRED_REPOS - repos)
    if missing_repos:
        raise VerticalSliceValidationError(f"missing sibling surface checks for: {missing_repos}")
    missing_surfaces = [
        f"{item.get('repo')}:{item.get('path')}"
        for item in checks
        if isinstance(item, dict) and item.get("status") != "present"
    ]
    if missing_surfaces:
        raise VerticalSliceValidationError(f"sibling surfaces missing: {missing_surfaces}")

    review = report.get("attorney_review_packet")
    if not isinstance(review, dict):
        raise VerticalSliceValidationError("attorney_review_packet must be an object")
    if not str(review.get("reliance_posture", "")).startswith("not_reliable"):
        raise VerticalSliceValidationError("reliance_posture must remain not_reliable")
    checklist = review.get("checklist")
    if not isinstance(checklist, list):
        raise VerticalSliceValidationError("attorney checklist must be a list")
    item_ids = {item.get("item_id") for item in checklist if isinstance(item, dict)}
    missing_items = sorted(REQUIRED_REVIEW_ITEMS - item_ids)
    if missing_items:
        raise VerticalSliceValidationError(f"attorney checklist missing: {missing_items}")
    prohibited = set(review.get("prohibited_actions") or [])
    missing_prohibited = sorted(PROHIBITED_ACTIONS - prohibited)
    if missing_prohibited:
        raise VerticalSliceValidationError(f"prohibited actions missing: {missing_prohibited}")

    blockers = report.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        raise VerticalSliceValidationError("blockers must be non-empty")
    for required in (
        "attorney_review:required_before_reliance",
        "owner_decision:required_before_any_real_data_or_production_use",
    ):
        if required not in blockers:
            raise VerticalSliceValidationError(f"missing blocker: {required}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        validate_report(_read_report(args.report))
    except VerticalSliceValidationError as exc:
        print(f"Intake vertical-slice demo validation failed: {exc}", file=sys.stderr)
        return 1
    print("Intake vertical-slice demo validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
