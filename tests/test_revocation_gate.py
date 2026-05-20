from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from lawfirm_os_orchestrator.commands.classify_exception import EXIT_POLICY, run

ROOT = Path(__file__).resolve().parents[1]


def _args(tmp_path: Path, **overrides):
    base = {
        "input": str(ROOT / "examples" / "synthetic_exception_event.json"),
        "substrate": str(ROOT / "tests" / "fixtures" / "substrate"),
        "ledger_dir": str(tmp_path / "ledger"),
        "packet_out": str(tmp_path / "runs"),
        "lake_mode": "disabled",
        "stdout": "json",
        "agent_control_source": "local_fixture",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _registry(tmp_path: Path, **updates) -> Path:
    raw = json.loads((ROOT / "config" / "agent_hostile" / "revocation_registry.json").read_text(encoding="utf-8"))
    raw.update(updates)
    path = tmp_path / "revocation_registry.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    return path


def test_revoked_agent_blocks_run(tmp_path: Path) -> None:
    code, summary = run(_args(tmp_path, agent_id="agent:revoked-demo"))

    assert code == EXIT_POLICY
    assert summary["gate"] == "RevocationGate"
    assert summary["reason_code"] == "agent_revoked"


def test_paused_route_blocks_action(tmp_path: Path) -> None:
    path = _registry(tmp_path, paused_routes=["route.workflow_escalation.v1"])
    code, summary = run(_args(tmp_path, revocation_registry=str(path)))

    assert code == EXIT_POLICY
    assert summary["gate"] == "RevocationGate"
    assert summary["reason_code"] == "route_paused"


def test_denied_tool_blocks_action(tmp_path: Path) -> None:
    path = _registry(tmp_path, denied_tools=["orchestrator.tool.synthetic_classify_exception.v1"])
    code, summary = run(_args(tmp_path, revocation_registry=str(path)))

    assert code == EXIT_POLICY
    assert summary["gate"] == "RevocationGate"
    assert summary["reason_code"] == "tool_denied"
