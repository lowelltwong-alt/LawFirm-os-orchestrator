from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.intake.owner_review import (
    IntakeOwnerReviewError,
    prepare_intake_owner_review_packet,
    write_intake_owner_review_artifacts,
)
from lawfirm_os_orchestrator.util.json_io import read_json


EXIT_INPUT_POLICY = 2
EXIT_ARTIFACT = 5


def run(args: Any) -> tuple[int, dict[str, Any]]:
    if args.intake_command != "prepare-owner-packet":
        return EXIT_INPUT_POLICY, {
            "status": "failed_validation",
            "error": f"unknown intake command: {args.intake_command}",
        }
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
