from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from lawfirm_os_orchestrator.commands.classify_exception import EXIT_POLICY, run
from lawfirm_os_orchestrator.security.endpoint_manifest import assert_no_default_open_surfaces

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


def _tool_manifest(tmp_path: Path, **tool_updates) -> Path:
    raw = json.loads((ROOT / "config" / "agent_hostile" / "tool_authority_manifest.json").read_text(encoding="utf-8"))
    raw["tools"][0].update(tool_updates)
    path = tmp_path / "tool_authority_manifest.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    return path


def test_unknown_unregistered_tool_blocks_action(tmp_path: Path) -> None:
    code, summary = run(_args(tmp_path, tool_id="classifier.unknown"))

    assert code == EXIT_POLICY
    assert summary["gate"] == "ToolAuthorityGate"
    assert summary["reason_code"] == "unknown_tool"


def test_default_open_tool_config_fails_validation(tmp_path: Path) -> None:
    path = _tool_manifest(tmp_path, auth_required=False)

    with pytest.raises(ValueError, match="auth_required=false"):
        assert_no_default_open_surfaces(path)

    code, summary = run(_args(tmp_path, tool_manifest=str(path)))
    assert code == EXIT_POLICY
    assert summary["gate"] == "ToolAuthorityGate"
    assert summary["reason_code"] == "tool_manifest_invalid"
    assert "auth_required=false" in summary["decision"]["details"]["error"]


def test_agent_callable_tool_requires_identity_and_audit(tmp_path: Path) -> None:
    path = _tool_manifest(tmp_path, agent_identity_required=False)
    with pytest.raises(ValueError, match="agent_identity_required=false"):
        assert_no_default_open_surfaces(path)

    path = _tool_manifest(tmp_path, audit_event_required=False)
    with pytest.raises(ValueError, match="audit_event_required=false"):
        assert_no_default_open_surfaces(path)
