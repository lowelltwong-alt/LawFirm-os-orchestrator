from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.discovery.models import DiscoverySignal
from lawfirm_os_orchestrator.evals.graders import read_json_line
from lawfirm_os_orchestrator.util.hashing import sha256_file
from lawfirm_os_orchestrator.util.json_io import read_json
from lawfirm_os_orchestrator.util.time import utc_now


def import_signal(input_path: Path, out_path: Path) -> DiscoverySignal:
    signal = load_local_signal(input_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("a", encoding="utf-8") as handle:
        handle.write(signal.model_dump_json() + "\n")
    return signal


def list_signals(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    signals: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        raw = read_json_line(line, path, line_number)
        signals.append(DiscoverySignal.model_validate(raw).model_dump(mode="json"))
    return signals


def load_local_signal(input_path: Path) -> DiscoverySignal:
    suffix = input_path.suffix.lower()
    if suffix == ".json":
        raw = read_json(input_path)
        if not isinstance(raw, dict):
            raise ValueError("Research signal JSON must be an object")
    elif suffix in {".md", ".markdown"}:
        raw = markdown_to_signal(input_path)
    else:
        raise ValueError("Research Radar local import supports only .json, .md, and .markdown files")

    enriched = {
        **raw,
        "source_path": str(input_path),
        "source_hash": sha256_file(input_path),
        "imported_at": utc_now(),
    }
    return DiscoverySignal.model_validate(enriched)


def markdown_to_signal(input_path: Path) -> dict[str, Any]:
    text = input_path.read_text(encoding="utf-8")
    title = next((line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")), input_path.stem)
    claim = " ".join(line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#"))
    if not claim:
        claim = f"Curated local research note: {title}"
    return {
        "signal_type": "external_research_discovery",
        "source_kind": "human_note",
        "source_tier": 3,
        "source_uri": input_path.resolve().as_uri(),
        "title": title,
        "published_at": None,
        "credibility": 0.5,
        "claims": [
            {
                "claim": claim[:500],
                "claim_type": "human_note",
                "evidence_strength": "medium",
            }
        ],
        "relevance": {
            "target_surfaces": ["evals"],
            "score": 0.5,
            "possible_upgrade": "Review local note for a proposal-only eval hypothesis.",
            "risk": "No autonomous code mutation.",
        },
        "recommended_action": "create_shadow_experiment",
    }
