from __future__ import annotations

from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.autonomy.assumption_mapper import load_green_lanes, map_signals_to_assumptions
from lawfirm_os_orchestrator.autonomy.risk_reclassifier import GreenLaneWatchResult, reclassify_lane
from lawfirm_os_orchestrator.research.research_signal_ingest import load_research_signals
from lawfirm_os_orchestrator.util.json_io import write_json


def watch_green_lanes(*, signals_path: Path, lanes_path: Path, out_path: Path) -> dict[str, Any]:
    lanes = load_green_lanes(lanes_path)
    signals = load_research_signals(signals_path)
    results: list[GreenLaneWatchResult] = []
    for lane in lanes:
        mappings = map_signals_to_assumptions(lane=lane, signals=signals)
        results.append(reclassify_lane(lane=lane, signals=signals, mappings=mappings))
    payload = {
        "schema_version": "1.0",
        "status": "ok",
        "local_artifact_only": True,
        "runs_git": False,
        "applies_patch": False,
        "writes_to_semantic_substrate": False,
        "lake_writes": False,
        "calls_model": False,
        "calls_network": False,
        "external_writes": False,
        "human_restoration_required": True,
        "may_restore_green": False,
        "results": [result.model_dump(mode="json") for result in results],
    }
    write_json(out_path, payload)
    return payload
