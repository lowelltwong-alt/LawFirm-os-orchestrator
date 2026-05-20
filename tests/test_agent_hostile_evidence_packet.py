from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from lawfirm_os_orchestrator.commands.classify_exception import run
from lawfirm_os_orchestrator.util.json_io import read_json

ROOT = Path(__file__).resolve().parents[1]


def test_evidence_packet_contains_agent_hostile_proof(tmp_path: Path) -> None:
    args = SimpleNamespace(
        input=str(ROOT / "examples" / "synthetic_exception_event.json"),
        substrate=str(ROOT / "tests" / "fixtures" / "substrate"),
        ledger_dir=str(tmp_path / "ledger"),
        packet_out=str(tmp_path / "runs"),
        lake_mode="disabled",
        stdout="json",
        agent_id="agent:packet-proof",
        delegating_user_id="user:reviewer",
        tenant_id="tenant.synthetic",
    )

    code, summary = run(args)

    assert code == 0
    packet_dir = Path(summary["evidence_packet_path"])
    packet = read_json(packet_dir / "packet.json")
    assert packet["agent_identity"]["agent_instance_id"] == "agent:packet-proof"
    assert packet["agent_identity"]["delegating_user_id"] == "user:reviewer"
    assert {d["gate"] for d in packet["authz_decisions"]} == {
        "AgentIdentityGate",
        "RevocationGate",
        "ToolAuthorityGate",
        "PromptIntegrityGate",
    }
    assert packet["prompt_integrity"]["prompt_ref"] == "orchestrator.prompt.classify_exception.synthetic.v1"
    assert packet["prompt_integrity"]["approved"] is True
    assert packet["revocation_snapshot"]["agent_revoked"] is False
    assert packet["blast_radius"]["tenant_id"] == "tenant.synthetic"
    assert "orchestrator.tool.synthetic_classify_exception.v1" in packet["blast_radius"]["tool_scope"]
    assert packet["agent_control_provenance"]["source"] == "substrate"
    assert packet["agent_control_provenance"]["canonical"] is True
    assert packet["agent_control_provenance"]["contract_sha"]
    assert "prompt" in packet["agent_control_provenance"]["registries"]

    manifest = read_json(packet_dir / "manifest.json")
    assert "agent_identity.json" in manifest["files"]
    assert "authz_decisions.json" in manifest["files"]
    assert "prompt_integrity.json" in manifest["files"]
    assert "revocation_snapshot.json" in manifest["files"]
    assert "blast_radius.json" in manifest["files"]
    assert "agent_control_provenance.json" in manifest["files"]
