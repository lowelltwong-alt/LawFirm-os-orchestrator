from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path

from lawfirm_os_orchestrator.autonomy.assumption_mapper import (
    GreenLanePassport,
    map_signal_to_assumptions,
)
from lawfirm_os_orchestrator.autonomy.green_lane_watcher import watch_green_lanes
from lawfirm_os_orchestrator.research.research_signal_ingest import ResearchSignal

ROOT = Path(__file__).resolve().parents[1]


def artifact_dir() -> Path:
    path = ROOT / ".lawfirm-os-orchestrator" / "test-artifacts" / f"pr03-{uuid.uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def lane_payload(status: str = "valid") -> dict[str, object]:
    return {
        "lane_id": "LANE-SYNTHETIC-FIXTURE-DRAFTS",
        "risk_color": "green",
        "description": "Synthetic fixture and local artifact drafting.",
        "source_refs": ["registry/autonomy-lane-registry.json"],
        "assumptions": [
            {
                "assumption_id": "ASM-000001",
                "statement": "Inputs remain synthetic and metadata-only.",
                "status": status,
                "keywords": ["synthetic", "metadata", "fixture"],
                "source_refs": ["schemas/autonomy/assumption-record.schema.json"],
            }
        ],
    }


def signal_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "signal_id": "SIG-PR03-001",
        "signal_type": "informational",
        "summary": "Unrelated local note.",
        "affected_assumption_ids": [],
        "keywords": ["unrelated"],
        "hard_red_triggers": [],
        "yellow_triggers": [],
        "evidence_refs": ["evidence://local/signal"],
        "source_refs": ["examples/research_signals/local_signal.json"],
    }
    payload.update(overrides)
    return payload


def write_case(lanes: list[dict[str, object]], signals: list[dict[str, object]]) -> tuple[Path, Path, Path]:
    root = artifact_dir()
    lanes_path = root / "lanes.json"
    signals_path = root / "signals.json"
    out_path = root / "watch.json"
    lanes_path.write_text(json.dumps({"lanes": lanes}), encoding="utf-8")
    signals_path.write_text(json.dumps({"signals": signals}), encoding="utf-8")
    return lanes_path, signals_path, out_path


def run_watch(lanes: list[dict[str, object]], signals: list[dict[str, object]]) -> dict[str, object]:
    lanes_path, signals_path, out_path = write_case(lanes, signals)
    result = watch_green_lanes(signals_path=signals_path, lanes_path=lanes_path, out_path=out_path)
    assert out_path.exists()
    return result


def first_result(result: dict[str, object]) -> dict[str, object]:
    return result["results"][0]  # type: ignore[index]


def test_unchanged_green_when_no_signal_affects_assumptions():
    result = first_result(run_watch([lane_payload()], [signal_payload()]))

    assert result["previous_color"] == "green"
    assert result["recommended_color"] == "green"
    assert result["affected_assumptions"] == []
    assert result["trigger_signals"] == []
    assert "no signal affected an assumption" in result["explanation"]


def test_green_to_yellow_on_assumption_uncertainty():
    result = first_result(
        run_watch(
            [lane_payload(status="uncertain")],
            [
                signal_payload(
                    signal_id="SIG-PR03-YELLOW",
                    signal_type="assumption_uncertainty",
                    summary="New local evidence weakens synthetic fixture assumption.",
                    affected_assumption_ids=["ASM-000001"],
                    yellow_triggers=["assumption_uncertainty"],
                )
            ],
        )
    )

    assert result["recommended_color"] == "yellow"
    assert result["affected_assumptions"] == ["ASM-000001"]
    assert result["trigger_signals"] == ["SIG-PR03-YELLOW"]
    assert result["human_restoration_required"] is True
    assert result["may_restore_green"] is False


def test_green_to_red_on_hard_red_trigger():
    result = first_result(
        run_watch(
            [lane_payload()],
            [
                signal_payload(
                    signal_id="SIG-PR03-RED",
                    signal_type="hard_red_trigger",
                    summary="Signal indicates real client data entered the green lane.",
                    affected_assumption_ids=["ASM-000001"],
                    hard_red_triggers=["real_client_data"],
                )
            ],
        )
    )

    assert result["recommended_color"] == "red"
    assert result["hard_red_triggers"] == ["real_client_data"]
    assert "execute final authority" in result["forbidden_next_actions"]


def test_hard_red_trigger_wins_over_yellow():
    result = first_result(
        run_watch(
            [lane_payload(status="weakened")],
            [
                signal_payload(
                    signal_id="SIG-PR03-RED-YELLOW",
                    signal_type="assumption_uncertainty",
                    summary="Uncertain assumption plus possible privileged content.",
                    affected_assumption_ids=["ASM-000001"],
                    yellow_triggers=["assumption_uncertainty"],
                    hard_red_triggers=["privileged_content"],
                )
            ],
        )
    )

    assert result["recommended_color"] == "red"
    assert result["hard_red_triggers"] == ["privileged_content"]
    assert "assumption_uncertainty" in result["yellow_triggers"]


def test_signal_maps_to_assumption_by_explicit_id_and_keyword():
    lane = GreenLanePassport.model_validate(lane_payload())
    explicit_signal = ResearchSignal.model_validate(signal_payload(affected_assumption_ids=["ASM-000001"]))
    keyword_signal = ResearchSignal.model_validate(signal_payload(summary="Synthetic fixture distribution changed."))

    explicit_mapping = map_signal_to_assumptions(lane, explicit_signal)
    keyword_mapping = map_signal_to_assumptions(lane, keyword_signal)

    assert explicit_mapping[0].assumption_id == "ASM-000001"
    assert explicit_mapping[0].signal_id == "SIG-PR03-001"
    assert keyword_mapping[0].assumption_id == "ASM-000001"


def test_explanation_includes_affected_assumption_and_signal():
    result = first_result(
        run_watch(
            [lane_payload(status="requires_review")],
            [
                signal_payload(
                    signal_id="SIG-PR03-EXPLAIN",
                    signal_type="eval_drift",
                    summary="Eval drift affects synthetic fixture assumption.",
                    affected_assumption_ids=["ASM-000001"],
                )
            ],
        )
    )

    assert "SIG-PR03-EXPLAIN" in result["explanation"]
    assert "ASM-000001" in result["explanation"]


def test_human_restoration_required_and_no_automatic_green_restoration():
    result = first_result(
        run_watch(
            [lane_payload()],
            [
                signal_payload(
                    signal_id="SIG-PR03-RESTORE",
                    signal_type="hard_red_trigger",
                    summary="Agent attempted human green restoration.",
                    affected_assumption_ids=["ASM-000001"],
                    indicates_green_restoration=True,
                )
            ],
        )
    )

    assert result["recommended_color"] == "red"
    assert result["human_restoration_required"] is True
    assert result["may_restore_green"] is False
    assert "restore green automatically" in result["forbidden_next_actions"]


def test_watcher_modules_do_not_import_network_model_or_git_execution_modules():
    source_paths = [
        ROOT / "src" / "lawfirm_os_orchestrator" / "autonomy" / "green_lane_watcher.py",
        ROOT / "src" / "lawfirm_os_orchestrator" / "autonomy" / "assumption_mapper.py",
        ROOT / "src" / "lawfirm_os_orchestrator" / "autonomy" / "risk_reclassifier.py",
        ROOT / "src" / "lawfirm_os_orchestrator" / "autonomy" / "red_flag_detector.py",
        ROOT / "src" / "lawfirm_os_orchestrator" / "research" / "research_signal_ingest.py",
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in source_paths)

    assert "subprocess" not in combined
    assert "socket" not in combined
    assert "requests" not in combined
    assert "httpx" not in combined
    assert "urllib" not in combined
    assert "openai" not in combined
    assert "git commit" not in combined
    assert "git push" not in combined


def test_cli_watch_green_lanes_writes_local_output_json():
    lanes_path, signals_path, out_path = write_case(
        [lane_payload(status="uncertain")],
        [
            signal_payload(
                signal_id="SIG-PR03-CLI",
                signal_type="assumption_uncertainty",
                summary="Assumption drift affects synthetic fixture.",
                affected_assumption_ids=["ASM-000001"],
            )
        ],
    )

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "lawfirm_os_orchestrator",
            "watch-green-lanes",
            "--signals",
            str(signals_path),
            "--lanes",
            str(lanes_path),
            "--out",
            str(out_path),
            "--stdout",
            "json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    output = json.loads(completed.stdout)

    assert output["status"] == "ok"
    assert output["runs_git"] is False
    assert output["calls_model"] is False
    assert output["calls_network"] is False
    assert output["writes_to_semantic_substrate"] is False
    assert output["lake_writes"] is False
    assert output["results"][0]["recommended_color"] == "yellow"
    assert out_path.exists()
