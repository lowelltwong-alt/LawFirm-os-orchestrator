from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from lawfirm_os_orchestrator.intake.vertical_slice_demo import (
    build_intake_vertical_slice_demo,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_intake_vertical_slice_demo.py"
FIXTURE = ROOT / "examples" / "intake_owner_review_request.synthetic.json"


def _report() -> dict:
    request = json.loads(FIXTURE.read_text(encoding="utf-8"))
    report = build_intake_vertical_slice_demo(
        request=request,
        workspace=ROOT.parent,
        owner_packet_ref="owner.json",
        lake_packet_ref="lake.json",
        generated_at="2026-07-06T00:00:00Z",
    )
    for item in report["sibling_surface_checks"]:
        item["exists"] = True
        item["status"] = "present"
    return report


def _run(report: dict, tmp_path: Path) -> subprocess.CompletedProcess[str]:
    path = tmp_path / "report.json"
    path.write_text(json.dumps(report), encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--report", str(path)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_vertical_slice_demo_validator_accepts_safe_report(tmp_path: Path) -> None:
    completed = _run(_report(), tmp_path)

    assert completed.returncode == 0, completed.stderr
    assert "validation passed" in completed.stdout


def test_vertical_slice_demo_validator_rejects_write_authority(tmp_path: Path) -> None:
    report = _report()
    report["no_write_controls"]["exception_lake_write_authorized"] = True

    completed = _run(report, tmp_path)

    assert completed.returncode != 0
    assert "exception_lake_write_authorized" in completed.stderr


def test_vertical_slice_demo_validator_rejects_missing_review_item(tmp_path: Path) -> None:
    report = _report()
    mutated = copy.deepcopy(report["attorney_review_packet"]["checklist"])
    report["attorney_review_packet"]["checklist"] = [
        item for item in mutated if item["item_id"] != "review_conflicts"
    ]

    completed = _run(report, tmp_path)

    assert completed.returncode != 0
    assert "review_conflicts" in completed.stderr
