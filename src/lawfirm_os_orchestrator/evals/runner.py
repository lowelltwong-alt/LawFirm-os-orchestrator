from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

from lawfirm_os_orchestrator.commands.classify_exception import run as run_classify_exception
from lawfirm_os_orchestrator.evals.graders import grade_case, load_gold_labels, read_json_line, summarize_grades
from lawfirm_os_orchestrator.substrate.reader import PathSubstrateClient
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.json_io import write_json


def load_eval_cases(path: Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = read_json_line(line, path, line_number)
        if "case_id" not in record or "input" not in record:
            raise ValueError(f"Eval record must include case_id and input at {path}:{line_number}")
        cases.append(record)
    if not cases:
        raise ValueError(f"No eval cases found: {path}")
    return cases


def run_eval_suite(
    *,
    fixture_path: Path,
    gold_path: Path,
    substrate_root: Path,
    artifact_root: Path,
) -> dict[str, Any]:
    cases = load_eval_cases(fixture_path)
    labels = load_gold_labels(gold_path)
    snapshot = PathSubstrateClient(substrate_root).load_snapshot()
    allowed_route_ids = set(snapshot.allowed_route_ids)
    allowed_event_classes = set(snapshot.allowed_event_classes)
    suite_artifact_root = artifact_root / new_id("eval_run")

    grades: list[dict[str, Any]] = []
    for case in cases:
        case_id = str(case["case_id"])
        if case_id not in labels:
            raise ValueError(f"Missing gold label for case_id: {case_id}")
        case_root = suite_artifact_root / case_id
        input_path = case_root / "input.json"
        write_json(input_path, case["input"])
        args = SimpleNamespace(
            input=str(input_path),
            substrate=str(substrate_root),
            ledger_dir=str(case_root / "ledger"),
            packet_out=str(case_root / "runs"),
            lake_mode="disabled",
            stdout="json",
        )
        code, summary = run_classify_exception(args)
        if code != 0:
            summary = {"status": summary.get("status", "failed"), "error": summary.get("error") or summary.get("reasons"), "confidence": 0.0}
        grades.append(
            grade_case(
                case_id=case_id,
                summary=summary,
                gold=labels[case_id],
                allowed_route_ids=allowed_route_ids,
                allowed_event_classes=allowed_event_classes,
            )
        )

    missing_cases = sorted(set(labels) - {str(case["case_id"]) for case in cases})
    if missing_cases:
        raise ValueError(f"Gold labels without fixtures: {', '.join(missing_cases)}")

    return {
        "schema_version": "1.0",
        "eval_name": "classify_exception",
        "fixture_path": str(fixture_path),
        "gold_path": str(gold_path),
        "substrate_manifest_id": snapshot.manifest.manifest_id,
        "substrate_manifest_hash": snapshot.manifest_hash,
        "metrics": summarize_grades(grades),
        "cases": grades,
    }
