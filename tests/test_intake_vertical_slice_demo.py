from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from lawfirm_os_orchestrator.intake.vertical_slice_demo import (
    build_intake_vertical_slice_demo,
)


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "intake_owner_review_request.synthetic.json"


def _fixture_payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _workspace(root: Path) -> Path:
    required = {
        "LawFirm-os-semantic-substrate": [
            "registry/governance-dependency-map.json",
            "registry/lawfirm-os-repo-registry.json",
        ],
        "LawFirm-os-intake": [
            "BUILD_VERIFICATION.md",
            "contracts.lock.json",
        ],
        "LawFirm-os-legal-knowledge-runtime": [
            "AI_WORK_START_HERE.md",
            "src/lawfirm_os_legal_knowledge/cli.py",
        ],
        "LawFirm-os-exceptions-lake-runtime": [
            "examples/legal_document_integrity_check_event.json",
        ],
        "LawFirm-os-skills-registry": [
            "registry/proposed-draft-skill-index.json",
        ],
    }
    for repo, paths in required.items():
        for rel in paths:
            path = root / repo / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("synthetic fixture\n", encoding="utf-8")
    return root


def test_vertical_slice_demo_reports_no_write_cross_repo_surface() -> None:
    report = build_intake_vertical_slice_demo(
        request=_fixture_payload(),
        workspace=ROOT.parent,
        owner_packet_ref="owner.json",
        lake_packet_ref="lake.json",
        generated_at="2026-07-06T00:00:00Z",
    )

    assert report["schema_version"] == "intake_vertical_slice_demo.v0_1"
    assert report["status"] == "blocked_pending_attorney_and_owner_review"
    assert report["synthetic"] is True
    assert report["non_authoritative"] is True
    assert report["no_write_controls"]["exception_lake_write_authorized"] is False
    assert report["no_write_controls"]["semantic_substrate_write_authorized"] is False
    assert report["no_write_controls"]["client_or_carrier_submission_authorized"] is False
    assert report["no_write_controls"]["model_call_authorized"] is False
    assert {item["repo"] for item in report["sibling_surface_checks"]} == {
        "LawFirm-os-semantic-substrate",
        "LawFirm-os-intake",
        "LawFirm-os-legal-knowledge-runtime",
        "LawFirm-os-exceptions-lake-runtime",
        "LawFirm-os-skills-registry",
    }
    assert "attorney_review:required_before_reliance" in report["blockers"]
    assert any(blocker.startswith("owner:") for blocker in report["blockers"])
    assert any(blocker.startswith("lake:") for blocker in report["blockers"])
    review_packet = report["attorney_review_packet"]
    assert review_packet["reliance_posture"].startswith("not_reliable")
    assert {item["item_id"] for item in review_packet["checklist"]} >= {
        "review_source_binding",
        "review_matter_posture",
        "review_conflicts",
        "review_budget",
        "review_lake_admission",
        "review_client_use",
    }
    assert "client_or_carrier_submission" in review_packet["prohibited_actions"]


def test_vertical_slice_demo_cli_writes_local_artifacts_only(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path / "workspace")
    out_dir = tmp_path / "out"
    ledger_dir = tmp_path / "ledger"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "lawfirm_os_orchestrator",
            "intake",
            "run-vertical-slice-demo",
            "--input",
            str(FIXTURE),
            "--workspace",
            str(workspace),
            "--out-dir",
            str(out_dir),
            "--ledger-dir",
            str(ledger_dir),
            "--stdout",
            "json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    summary = json.loads(completed.stdout)
    assert summary["status"] == "blocked_pending_attorney_and_owner_review"
    assert summary["sibling_surface_status"] == "passed"
    assert summary["external_write_authorized"] is False
    assert summary["exception_lake_write_authorized"] is False
    assert summary["not_authorized_for_client_submission"] is True
    assert Path(summary["report_path"]).exists()
    assert Path(summary["markdown_path"]).exists()
    markdown = Path(summary["markdown_path"]).read_text(encoding="utf-8")
    assert "## Attorney Review Checklist" in markdown
    assert "## Prohibited Actions" in markdown
    assert Path(summary["owner_packet_path"]).exists()
    assert Path(summary["lake_packet_path"]).exists()
    ledger_lines = Path(summary["ledger_path"]).read_text(encoding="utf-8").splitlines()
    assert len(ledger_lines) == 1
    ledger_record = json.loads(ledger_lines[0])
    assert ledger_record["command_name"] == "intake run-vertical-slice-demo"
    assert ledger_record["exception_lake_write_authorized"] is False
