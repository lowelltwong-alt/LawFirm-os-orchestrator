from __future__ import annotations

from pathlib import Path

from lawfirm_os_orchestrator.policy.agent_hostile_controls import validate_tool_authority_manifest


def assert_no_default_open_surfaces(tool_manifest_path: str | Path) -> None:
    validate_tool_authority_manifest(tool_manifest_path)
