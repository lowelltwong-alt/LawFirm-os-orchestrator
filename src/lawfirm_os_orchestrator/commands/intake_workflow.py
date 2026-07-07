from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.intake.lake_admission_review import (
    IntakeLakeAdmissionReviewError,
    prepare_intake_lake_admission_review_packet,
    write_intake_lake_admission_review_artifacts,
)
from lawfirm_os_orchestrator.intake.owner_review import (
    IntakeOwnerReviewError,
    prepare_intake_owner_review_packet,
    write_intake_owner_review_artifacts,
)
from lawfirm_os_orchestrator.intake.vertical_slice_demo import (
    write_intake_vertical_slice_demo_artifacts,
)
from lawfirm_os_orchestrator.util.json_io import read_json


EXIT_INPUT_POLICY = 2
EXIT_ARTIFACT = 5


def run(args: Any) -> tuple[int, dict[str, Any]]:
    if args.intake_command == "prepare-owner-packet":
        try:
            request = read_json(Path(args.input))
            packet = prepare_intake_owner_review_packet(request)
        except (OSError, IntakeOwnerReviewError, ValueError, TypeError) as exc:
            return EXIT_INPUT_POLICY, {"status": "failed_validation", "error": str(exc)}

        try:
            summary = write_intake_owner_review_artifacts(
                packet=packet,
                out_dir=Path(args.out_dir),
                ledger_dir=Path(args.ledger_dir),
            )
        except OSError as exc:
            return EXIT_ARTIFACT, {"status": "artifact_failed", "error": str(exc)}
        return 0, summary

    if args.intake_command == "build-lake-admission-review-packet":
        try:
            owner_packet = read_json(Path(args.owner_packet))
            packet = prepare_intake_lake_admission_review_packet(owner_packet)
        except (OSError, IntakeLakeAdmissionReviewError, ValueError, TypeError) as exc:
            return EXIT_INPUT_POLICY, {"status": "failed_validation", "error": str(exc)}

        try:
            summary = write_intake_lake_admission_review_artifacts(
                packet=packet,
                out_dir=Path(args.out_dir),
                ledger_dir=Path(args.ledger_dir),
            )
        except OSError as exc:
            return EXIT_ARTIFACT, {"status": "artifact_failed", "error": str(exc)}
        return 0, summary

    if args.intake_command == "run-vertical-slice-demo":
        try:
            request = read_json(Path(args.input))
            summary = write_intake_vertical_slice_demo_artifacts(
                request=request,
                workspace=Path(args.workspace),
                out_dir=Path(args.out_dir),
                ledger_dir=Path(args.ledger_dir),
            )
        except (
            OSError,
            IntakeOwnerReviewError,
            IntakeLakeAdmissionReviewError,
            ValueError,
            TypeError,
        ) as exc:
            return EXIT_INPUT_POLICY, {"status": "failed_validation", "error": str(exc)}
        return 0, summary

    else:
        return EXIT_INPUT_POLICY, {
            "status": "failed_validation",
            "error": f"unknown intake command: {args.intake_command}",
        }
