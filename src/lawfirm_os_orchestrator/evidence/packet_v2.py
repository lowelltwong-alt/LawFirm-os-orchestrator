"""EvidencePacket v2 builder (PR-05).

V2 makes EvidencePacket the full cross-boundary unit:
  - authority lock        (contract_surface_sha256 binding)
  - context bundle ref    (id + hash)
  - execution authority   (Request/Decision/Passport/Result hash quads, one per bounded action)
  - SourceRef list        (provenance refs from Legal Knowledge Runtime)
  - ClaimRef list         (claim support/verification refs)
  - CoverageRecord list   (how much of each source was read)
  - VerificationRecord    (claim verification outcomes)
  - approval records      (human approvals attached to the run)
  - defect records        (defects detected during the run)
  - hash chain            (every reference is content-addressed)

Lives alongside the v1 builder in packet.py to keep the existing v1 test
surface unchanged. The orchestrator wires v2 into the run flow in a
follow-up PR; PR-05 ships the builder and store-side admission.

Substrate schema: schemas/evidence-packet.v2.schema.json (evidence-packet-v2).
"""
from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable, Sequence

from lawfirm_os_orchestrator.util.hashing import canonical_json, sha256_file
from lawfirm_os_orchestrator.util.json_io import write_json


SCHEMA_VERSION = "evidence_packet.v2"


def evidence_packet_hash(payload: dict[str, Any]) -> str:
    """Bare-hex SHA-256 of canonical-JSON payload with evidence_packet_hash field excluded.

    Mirrors the fix in commit 7bf7fd7 (compute hash from payload-without-self-hash).
    """
    clean = {k: v for k, v in payload.items() if k != "evidence_packet_hash"}
    return hashlib.sha256(canonical_json(clean)).hexdigest()


def _iso_utc_now() -> str:
    return datetime.now(tz=UTC).isoformat().replace("+00:00", "Z")


def manifest_hash_for_dir(packet_dir: Path) -> tuple[str, dict[str, str]]:
    """Hash an artifact manifest covering every file in the packet_dir, EXCEPT
    packet.json and manifest.json themselves. Returns (manifest_sha256, files_map).
    files_map is sha256 hex digests keyed by relative filename, sorted.
    """
    files: dict[str, str] = {}
    if packet_dir.exists():
        for child in sorted(packet_dir.iterdir()):
            if not child.is_file():
                continue
            if child.name in ("packet.json", "manifest.json"):
                continue
            files[child.name] = sha256_file(child).removeprefix("sha256:")
    digest = hashlib.sha256(canonical_json(files)).hexdigest()
    return digest, files


def build_evidence_packet_v2(
    *,
    evidence_packet_id: str,
    contract_surface_sha256: str,
    context_bundle_id: str,
    context_bundle_hash: str,
    execution_authority_records: Sequence[dict[str, str]],
    source_refs: Sequence[dict[str, Any]] = (),
    claim_refs: Sequence[dict[str, Any]] = (),
    coverage_records: Sequence[dict[str, Any]] = (),
    verification_records: Sequence[dict[str, Any]] = (),
    approval_records: Sequence[dict[str, Any]] = (),
    defect_records: Sequence[dict[str, Any]] = (),
    manifest_hash: str,
    generated_at: str | None = None,
    run_id: str,
    source_repo: str = "LawFirm-os-orchestrator",
) -> dict[str, Any]:
    """Build a v2 EvidencePacket payload. Returns the dict ready to write to packet.json.

    `execution_authority_records` is required and must be non-empty: every packet
    must reference at least one Request/Decision (Passport/Result optional for
    denied actions). Each record is a dict with these keys:
      - execution_request_hash      (required, 64-hex)
      - execution_decision_hash     (required, 64-hex)
      - execution_passport_hash     (optional, 64-hex)
      - execution_result_hash       (optional, 64-hex)
    """
    if not execution_authority_records:
        raise ValueError(
            "v2 EvidencePacket requires at least one execution authority record (every bounded action covered)"
        )
    for rec in execution_authority_records:
        if not rec.get("execution_request_hash") or not rec.get("execution_decision_hash"):
            raise ValueError(
                "every execution authority record must include execution_request_hash and execution_decision_hash"
            )
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "evidence_packet_id": evidence_packet_id,
        "contract_surface_sha256": contract_surface_sha256,
        "context_bundle_ref": {
            "context_bundle_id": context_bundle_id,
            "context_bundle_hash": context_bundle_hash,
        },
        "execution_authority_records": [dict(r) for r in execution_authority_records],
        "source_refs": [dict(r) for r in source_refs],
        "claim_refs": [dict(r) for r in claim_refs],
        "coverage_records": [dict(r) for r in coverage_records],
        "verification_records": [dict(r) for r in verification_records],
        "approval_records": [dict(r) for r in approval_records],
        "defect_records": [dict(r) for r in defect_records],
        "manifest_hash": manifest_hash,
        "generated_at": generated_at or _iso_utc_now(),
        "run_id": run_id,
        "source_repo": source_repo,
    }
    payload["evidence_packet_hash"] = evidence_packet_hash(payload)
    return payload


def write_evidence_packet_v2(packet_dir: Path, packet: dict[str, Any]) -> None:
    """Write packet.json and manifest.json to packet_dir."""
    packet_dir.mkdir(parents=True, exist_ok=True)
    write_json(packet_dir / "packet.json", packet)
    files_manifest = {
        "schema_version": "evidence_packet_manifest.v2",
        "evidence_packet_id": packet["evidence_packet_id"],
        "evidence_packet_hash": packet["evidence_packet_hash"],
        "manifest_hash": packet["manifest_hash"],
        "files": {name: sha for name, sha in sorted(_iter_artifact_files(packet_dir).items())},
    }
    write_json(packet_dir / "manifest.json", files_manifest)


def _iter_artifact_files(packet_dir: Path) -> dict[str, str]:
    files: dict[str, str] = {}
    for child in sorted(packet_dir.iterdir()):
        if not child.is_file():
            continue
        if child.name in ("packet.json", "manifest.json"):
            continue
        files[child.name] = sha256_file(child).removeprefix("sha256:")
    return files
