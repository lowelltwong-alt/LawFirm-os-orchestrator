from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from lawfirm_os_orchestrator.commands.classify_exception import run
from lawfirm_os_orchestrator.evidence.packet import packet_content_hash
from lawfirm_os_orchestrator.util.hashing import sha256_file
from lawfirm_os_orchestrator.util.json_io import read_json

ROOT = Path(__file__).resolve().parents[1]
SUBSTRATE = ROOT.parent / "LawFirm-os-semantic-substrate"


def test_real_sibling_substrate_classify_exception_dry_run_packet_integrity(tmp_path: Path) -> None:
    assert SUBSTRATE.exists(), "sibling Semantic Substrate checkout is required"
    args = SimpleNamespace(
        input=str(ROOT / "examples" / "synthetic_exception_event.json"),
        substrate=str(SUBSTRATE),
        ledger_dir=str(tmp_path / "ledger"),
        packet_out=str(tmp_path / "runs"),
        lake_mode="dry-run",
        stdout="json",
    )

    code, summary = run(args)

    assert code == 0
    packet_dir = Path(summary["evidence_packet_path"])
    packet_path = packet_dir / "packet.json"
    manifest_path = packet_dir / "manifest.json"
    packet = read_json(packet_path)
    manifest = read_json(manifest_path)

    assert summary["manifest_id"] == "lawfirm-os-semantic-substrate-orchestrator-manifest-v1"
    assert packet["contract_lock"]["validated_ref_type"] == "git_sha"
    assert packet["contract_lock"]["validated_ref"] == "43991155f0286e6d8bc5ba0bfe6b42407b1b3f12"
    assert packet["packet_hash"] == packet_content_hash(packet)
    assert manifest["packet_hash"] == packet["packet_hash"]
    assert manifest["files"]["packet.json"] == sha256_file(packet_path)
    assert "ingest_request.json" in manifest["files"]
    assert "ingest_receipt.json" in manifest["files"]
    assert "stdout_summary.json" in manifest["files"]
