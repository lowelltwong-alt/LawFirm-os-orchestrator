from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.util.json_io import read_json

HIGH_CONFIDENCE_THRESHOLD = 0.8
REQUIRED_EVIDENCE_FILES = {
    "manifest.json",
    "packet.json",
    "input_event.json",
    "classification_result.json",
    "validation_results.json",
}


@dataclass(frozen=True)
class GoldLabel:
    case_id: str
    route_id: str
    event_class: str


def load_gold_labels(path: Path) -> dict[str, GoldLabel]:
    labels: dict[str, GoldLabel] = {}
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        raw = read_json_line(line, path, line_number)
        label = GoldLabel(case_id=raw["case_id"], route_id=raw["route_id"], event_class=raw["event_class"])
        if label.case_id in labels:
            raise ValueError(f"Duplicate gold case_id: {label.case_id}")
        labels[label.case_id] = label
    return labels


def read_json_line(line: str, path: Path, line_number: int) -> dict[str, Any]:
    import json

    try:
        raw = json.loads(line)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError(f"JSONL record must be an object at {path}:{line_number}")
    return raw


def evidence_complete(packet_dir: Path) -> bool:
    if not packet_dir.exists():
        return False
    present = {child.name for child in packet_dir.iterdir() if child.is_file()}
    if not REQUIRED_EVIDENCE_FILES.issubset(present):
        return False
    packet = read_json(packet_dir / "packet.json")
    manifest = read_json(packet_dir / "manifest.json")
    return bool(
        packet.get("manifest_hash")
        and packet.get("trace_id")
        and packet.get("source_claim_refs")
        and packet.get("validation_results")
        and packet.get("packet_hash")
        and manifest.get("files")
    )


def count_model_calls(ledger_path: Path) -> int:
    if not ledger_path.exists():
        return 0
    calls = 0
    for line_number, line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        record = read_json_line(line, ledger_path, line_number)
        if record.get("step_type") == "model_call":
            calls += 1
    return calls


def grade_case(
    *,
    case_id: str,
    summary: dict[str, Any],
    gold: GoldLabel,
    allowed_route_ids: set[str],
    allowed_event_classes: set[str],
) -> dict[str, Any]:
    predicted_route = summary.get("route_id")
    predicted_event_class = summary.get("event_class")
    route_allowed = predicted_route in allowed_route_ids
    event_class_allowed = predicted_event_class in allowed_event_classes
    route_exact = route_allowed and predicted_route == gold.route_id
    event_class_exact = event_class_allowed and predicted_event_class == gold.event_class
    evidence_ok = evidence_complete(Path(str(summary.get("evidence_packet_path", ""))))
    model_calls = count_model_calls(Path(str(summary.get("ledger_path", ""))))
    confidence = float(summary.get("confidence") or 0.0)
    first_pass_validation = summary.get("status") == "ok" and route_allowed and event_class_allowed and evidence_ok
    high_confidence_error = confidence >= HIGH_CONFIDENCE_THRESHOLD and not (route_exact and event_class_exact)
    return {
        "case_id": case_id,
        "status": summary.get("status"),
        "route_exact_match": route_exact,
        "event_class_exact_match": event_class_exact,
        "first_pass_validation": first_pass_validation,
        "evidence_complete": evidence_ok,
        "high_confidence_error": high_confidence_error,
        "model_calls": model_calls,
        "predicted_route_id": predicted_route,
        "gold_route_id": gold.route_id,
        "predicted_event_class": predicted_event_class,
        "gold_event_class": gold.event_class,
        "confidence": confidence,
    }


def summarize_grades(grades: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(grades)
    if total == 0:
        raise ValueError("Cannot summarize zero eval grades")

    def rate(field: str) -> float:
        return sum(1 for grade in grades if grade[field]) / total

    return {
        "total_cases": total,
        "route_exact_match_rate": rate("route_exact_match"),
        "event_class_exact_match_rate": rate("event_class_exact_match"),
        "first_pass_validation_rate": rate("first_pass_validation"),
        "evidence_completeness_rate": rate("evidence_complete"),
        "high_confidence_error_count": sum(1 for grade in grades if grade["high_confidence_error"]),
        "high_confidence_error_rate": rate("high_confidence_error"),
        "high_confidence_threshold": HIGH_CONFIDENCE_THRESHOLD,
        "average_model_calls_per_run": sum(int(grade["model_calls"]) for grade in grades) / total,
    }
