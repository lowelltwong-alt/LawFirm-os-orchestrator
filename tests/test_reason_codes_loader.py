"""Tests for the orchestrator-side substrate reason-codes loader (PR-05.5)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from lawfirm_os_orchestrator.substrate import reason_codes as rc

REPO_ROOT = Path(__file__).resolve().parents[1]
SUBSTRATE = REPO_ROOT.parent / "LawFirm-os-semantic-substrate"
REGISTRY = SUBSTRATE / "registry" / "runtime-reason-codes-registry.json"


def _registry_vocab(name: str) -> set[str]:
    return set(json.loads(REGISTRY.read_text(encoding="utf-8"))["vocabularies"][name]["values"])


def test_module_imports_only_when_substrate_registry_exists() -> None:
    # The fact that 'from lawfirm_os_orchestrator.substrate import reason_codes as rc'
    # succeeded at top of file proves the fail-closed loader ran without error.
    assert hasattr(rc, "EXECUTION_DECISION_REASON_CODES")
    assert hasattr(rc, "SEMANTIC_MUTATION_ACTIONS")


def test_constants_match_registry_execution_decision_reason_codes() -> None:
    expected = _registry_vocab("execution_decision.reason_codes")
    assert rc.EXECUTION_DECISION_REASON_CODES == frozenset(expected)
    for value in expected:
        const_name = value.upper()
        assert getattr(rc, const_name) == value, f"{const_name} must equal {value!r}"


def test_constants_match_registry_semantic_mutation_actions() -> None:
    expected = _registry_vocab("runtime.semantic_mutation_actions")
    assert rc.SEMANTIC_MUTATION_ACTIONS == frozenset(expected)


def test_is_registered_reason_code_helpers() -> None:
    for code in rc.EXECUTION_DECISION_REASON_CODES:
        assert rc.is_registered_reason_code(code) is True
    assert rc.is_registered_reason_code("not_a_real_code") is False


def test_is_semantic_mutation_action_helpers() -> None:
    for action in rc.SEMANTIC_MUTATION_ACTIONS:
        assert rc.is_semantic_mutation_action(action) is True
    assert rc.is_semantic_mutation_action("not_an_action") is False


def test_loader_raises_for_missing_registry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """If LFOS_SUBSTRATE_PATH points at a directory without the registry, the
    loader must fail closed rather than fall back to hardcoded values."""
    fake_substrate = tmp_path / "fake-substrate"
    fake_substrate.mkdir()
    monkeypatch.setenv("LFOS_SUBSTRATE_PATH", str(fake_substrate))
    # Force a fresh module load with the patched env var.
    import importlib
    import sys
    sys.modules.pop("lawfirm_os_orchestrator.substrate.reason_codes", None)
    with pytest.raises(Exception) as exc_info:
        importlib.import_module("lawfirm_os_orchestrator.substrate.reason_codes")
    assert "runtime-reason-codes-registry" in str(exc_info.value)


def test_loader_raises_for_malformed_registry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    fake_substrate = tmp_path / "fake-substrate"
    (fake_substrate / "registry").mkdir(parents=True)
    (fake_substrate / "registry" / "runtime-reason-codes-registry.json").write_text(
        '{"vocabularies": {"x": {"values": "not-a-list"}}}\n', encoding="utf-8"
    )
    monkeypatch.setenv("LFOS_SUBSTRATE_PATH", str(fake_substrate))
    import importlib
    import sys
    sys.modules.pop("lawfirm_os_orchestrator.substrate.reason_codes", None)
    with pytest.raises(Exception) as exc_info:
        importlib.import_module("lawfirm_os_orchestrator.substrate.reason_codes")
    assert "list of string values" in str(exc_info.value)
