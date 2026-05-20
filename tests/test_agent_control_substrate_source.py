from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from lawfirm_os_orchestrator.commands.classify_exception import EXIT_POLICY, run
from lawfirm_os_orchestrator.policy.agent_hostile_controls import (
    DEFAULT_CLASSIFIER_TOOL_ID,
    DEFAULT_CLASSIFY_PROMPT_REF,
)
from lawfirm_os_orchestrator.util.hashing import sha256_text_file_lf
from lawfirm_os_orchestrator.util.json_io import read_json

ROOT = Path(__file__).resolve().parents[1]


def _args(tmp_path: Path, **overrides):
    base = {
        "input": str(ROOT / "examples" / "synthetic_exception_event.json"),
        "substrate": str(ROOT / "tests" / "fixtures" / "substrate"),
        "ledger_dir": str(tmp_path / "ledger"),
        "packet_out": str(tmp_path / "runs"),
        "lake_mode": "disabled",
        "stdout": "json",
        "agent_control_source": "substrate",
        "agent_control_substrate": str(_substrate_controls(tmp_path)),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _substrate_controls(tmp_path: Path) -> Path:
    root = tmp_path / "LawFirm-os-semantic-substrate"
    registry = root / "registry"
    registry.mkdir(parents=True, exist_ok=True)
    prompt_hash = sha256_text_file_lf(ROOT / "prompts" / "runtime" / "classify_exception_system.txt")
    (registry / "prompt-registry.json").write_text(
        json.dumps(
            {
                "prompts": [
                    {
                        "prompt_ref": DEFAULT_CLASSIFY_PROMPT_REF,
                        "prompt_version": "1.0.0",
                        "prompt_sha256": prompt_hash,
                        "prompt_approved": True,
                        "policy_bundle_id": "runtime-policy-v1",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (registry / "tool-authority-registry.json").write_text(
        json.dumps(
            {
                "tools": [
                    {
                        "tool_id": DEFAULT_CLASSIFIER_TOOL_ID,
                        "version": "1.0.0",
                        "risk_class": "transform",
                        "input_schema_ref": "exception-event-v1",
                        "output_schema_ref": "evidence-packet-v2",
                        "allowed_actor_types": ["agent"],
                        "auth_required": True,
                        "agent_identity_required": True,
                        "audit_event_required": True,
                        "approval_policy": {"approval_required": False, "approval_policy_id": "synthetic-preapproved"},
                        "allowed_data_classes": ["synthetic_fixture"],
                        "timeout_seconds": 30,
                        "retry_policy_ref": "retry.policy.none.mvp.v1",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    for name in (
        "endpoint-authority-registry.json",
        "agent-hostile-control-registry.json",
        "agent-control-contract-export.json",
    ):
        (registry / name).write_text("{}\n", encoding="utf-8")
    return root


def test_substrate_source_preferred_over_local_fixture_override(tmp_path: Path) -> None:
    local_prompt = tmp_path / "local_prompt_registry.json"
    local_prompt.write_text(
        json.dumps(
            {
                "prompts": [
                    {
                        "prompt_ref": DEFAULT_CLASSIFY_PROMPT_REF,
                        "prompt_version": "1.0.0",
                        "prompt_sha256": "sha256:" + "0" * 64,
                        "approved": False,
                        "policy_bundle_id": "runtime-policy-v1",
                        "prompt_file": "prompts/runtime/classify_exception_system.txt",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    code, summary = run(_args(tmp_path, prompt_registry=str(local_prompt)))

    assert code == 0
    packet = read_json(Path(summary["evidence_packet_path"]) / "packet.json")
    assert packet["agent_control_provenance"]["source"] == "substrate"
    assert packet["agent_control_provenance"]["canonical"] is True


def test_missing_substrate_registry_fails_closed_in_non_fixture_mode(tmp_path: Path) -> None:
    missing = tmp_path / "missing-semantic-substrate"
    missing.mkdir()

    code, summary = run(_args(tmp_path, agent_control_substrate=str(missing)))

    assert code == EXIT_POLICY
    assert summary["gate"] == "AgentControlRegistrySource"
    assert summary["reason_code"] == "tool_manifest_invalid"
    assert "Missing canonical Semantic Substrate agent-control registries" in summary["error"]


def test_local_fixture_mode_records_non_canonical_provenance(tmp_path: Path) -> None:
    code, summary = run(_args(tmp_path, agent_control_source="local_fixture"))

    assert code == 0
    packet = read_json(Path(summary["evidence_packet_path"]) / "packet.json")
    assert packet["agent_control_provenance"]["source"] == "local_fixture"
    assert packet["agent_control_provenance"]["canonical"] is False
    assert packet["agent_control_provenance"]["fixture_only"] is True
