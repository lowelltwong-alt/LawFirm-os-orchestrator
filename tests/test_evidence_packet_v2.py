"""Tests for the PR-05 EvidencePacket v2 builder."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from lawfirm_os_orchestrator.evidence.packet_v2 import (
    build_evidence_packet_v2,
    evidence_packet_hash,
    manifest_hash_for_dir,
    write_evidence_packet_v2,
)


SURFACE = "9787216aae3f0ef343009f961addce8cc5fcb6697b9a40243ff0176a3e4d0b34"
FIXED_AT = "2026-05-18T00:00:00Z"


def _minimal_packet(packet_dir: Path | None = None) -> dict:
    mh = "0" * 64
    if packet_dir is not None:
        mh, _ = manifest_hash_for_dir(packet_dir)
    return build_evidence_packet_v2(
        evidence_packet_id="pkt-1",
        contract_surface_sha256=SURFACE,
        context_bundle_id="ctx-1",
        context_bundle_hash="a" * 64,
        execution_authority_records=[
            {
                "execution_request_hash": "b" * 64,
                "execution_decision_hash": "c" * 64,
                "execution_passport_hash": "d" * 64,
                "execution_result_hash": "e" * 64,
            }
        ],
        source_refs=[{"source_ref_id": "sref-1"}],
        claim_refs=[{"claim_ref_id": "cref-1"}],
        coverage_records=[{"coverage_record_id": "cov-1"}],
        verification_records=[{"verification_record_id": "vrec-1"}],
        approval_records=[],
        defect_records=[],
        manifest_hash=mh,
        generated_at=FIXED_AT,
        run_id="run-1",
    )


def test_packet_hash_is_64_hex_and_excludes_itself() -> None:
    p1 = _minimal_packet()
    p2 = _minimal_packet()
    assert len(p1["evidence_packet_hash"]) == 64
    assert all(c in "0123456789abcdef" for c in p1["evidence_packet_hash"])
    assert p1["evidence_packet_hash"] == p2["evidence_packet_hash"], "identical inputs => identical hash"
    # Recomputing from payload-without-self-hash must match the stored hash.
    assert evidence_packet_hash(p1) == p1["evidence_packet_hash"]


def test_packet_hash_changes_when_any_section_changes() -> None:
    p1 = _minimal_packet()
    # Mutate a defect record
    p2 = build_evidence_packet_v2(
        evidence_packet_id="pkt-1",
        contract_surface_sha256=SURFACE,
        context_bundle_id="ctx-1",
        context_bundle_hash="a" * 64,
        execution_authority_records=p1["execution_authority_records"],
        source_refs=p1["source_refs"],
        claim_refs=p1["claim_refs"],
        coverage_records=p1["coverage_records"],
        verification_records=p1["verification_records"],
        approval_records=p1["approval_records"],
        defect_records=[{"defect_record_id": "def-1"}],  # added
        manifest_hash=p1["manifest_hash"],
        generated_at=FIXED_AT,
        run_id="run-1",
    )
    assert p1["evidence_packet_hash"] != p2["evidence_packet_hash"]


def test_at_least_one_execution_authority_record_required() -> None:
    with pytest.raises(ValueError, match="execution authority"):
        build_evidence_packet_v2(
            evidence_packet_id="pkt-1",
            contract_surface_sha256=SURFACE,
            context_bundle_id="ctx-1",
            context_bundle_hash="a" * 64,
            execution_authority_records=[],
            manifest_hash="0" * 64,
            run_id="run-1",
            generated_at=FIXED_AT,
        )


def test_execution_authority_record_needs_request_and_decision_hashes() -> None:
    with pytest.raises(ValueError, match="execution_request_hash"):
        build_evidence_packet_v2(
            evidence_packet_id="pkt-1",
            contract_surface_sha256=SURFACE,
            context_bundle_id="ctx-1",
            context_bundle_hash="a" * 64,
            execution_authority_records=[{"execution_passport_hash": "x" * 64}],
            manifest_hash="0" * 64,
            run_id="run-1",
            generated_at=FIXED_AT,
        )


def test_manifest_hash_is_stable_and_covers_artifacts(tmp_path: Path) -> None:
    (tmp_path / "input_event.json").write_text(json.dumps({"x": 1}) + "\n", encoding="utf-8")
    (tmp_path / "model_response.json").write_text(json.dumps({"y": 2}) + "\n", encoding="utf-8")
    digest1, files1 = manifest_hash_for_dir(tmp_path)
    digest2, files2 = manifest_hash_for_dir(tmp_path)
    assert digest1 == digest2
    assert set(files1) == {"input_event.json", "model_response.json"}
    # Mutate an artifact => digest must change.
    (tmp_path / "input_event.json").write_text(json.dumps({"x": 999}) + "\n", encoding="utf-8")
    digest3, _ = manifest_hash_for_dir(tmp_path)
    assert digest1 != digest3


def test_write_evidence_packet_v2_produces_packet_and_manifest(tmp_path: Path) -> None:
    (tmp_path / "input_event.json").write_text(json.dumps({"x": 1}) + "\n", encoding="utf-8")
    packet = _minimal_packet(tmp_path)
    write_evidence_packet_v2(tmp_path, packet)
    assert (tmp_path / "packet.json").is_file()
    assert (tmp_path / "manifest.json").is_file()
    reloaded = json.loads((tmp_path / "packet.json").read_text(encoding="utf-8"))
    assert reloaded["evidence_packet_hash"] == packet["evidence_packet_hash"]
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["evidence_packet_hash"] == packet["evidence_packet_hash"]
    assert manifest["manifest_hash"] == packet["manifest_hash"]
    assert "input_event.json" in manifest["files"]


def test_v2_packet_carries_authority_lock_and_context_bundle_ref() -> None:
    packet = _minimal_packet()
    assert packet["contract_surface_sha256"] == SURFACE
    assert packet["context_bundle_ref"]["context_bundle_id"] == "ctx-1"
    assert packet["context_bundle_ref"]["context_bundle_hash"] == "a" * 64


# ---------- PR-05.5 tightened coverage: every required field + every section ----------


def test_v2_packet_carries_required_top_level_fields() -> None:
    packet = _minimal_packet()
    assert packet["schema_version"] == "evidence_packet.v2"
    assert packet["source_repo"] == "LawFirm-os-orchestrator"
    assert packet["run_id"] == "run-1"
    assert packet["evidence_packet_id"] == "pkt-1"
    assert packet["generated_at"] == FIXED_AT


def _base_kwargs(packet_dir=None):
    mh = "0" * 64
    if packet_dir is not None:
        mh, _ = manifest_hash_for_dir(packet_dir)
    return dict(
        evidence_packet_id="pkt-1",
        contract_surface_sha256=SURFACE,
        context_bundle_id="ctx-1",
        context_bundle_hash="a" * 64,
        execution_authority_records=[
            {"execution_request_hash": "b" * 64, "execution_decision_hash": "c" * 64}
        ],
        source_refs=[{"source_ref_id": "sref-1"}],
        claim_refs=[{"claim_ref_id": "cref-1"}],
        coverage_records=[{"coverage_record_id": "cov-1"}],
        verification_records=[{"verification_record_id": "vrec-1"}],
        approval_records=[{"approval_record_id": "appr-1"}],
        defect_records=[{"defect_record_id": "def-1"}],
        manifest_hash=mh,
        generated_at=FIXED_AT,
        run_id="run-1",
    )


@pytest.mark.parametrize(
    "section, mutation",
    [
        ("source_refs", [{"source_ref_id": "sref-2"}, {"source_ref_id": "sref-3"}]),
        ("claim_refs", [{"claim_ref_id": "cref-2"}]),
        ("coverage_records", [{"coverage_record_id": "cov-2"}]),
        ("verification_records", [{"verification_record_id": "vrec-2"}]),
        ("approval_records", [{"approval_record_id": "appr-2"}]),
        ("defect_records", [{"defect_record_id": "def-2"}]),
        ("execution_authority_records", [
            {"execution_request_hash": "1" * 64, "execution_decision_hash": "2" * 64},
            {"execution_request_hash": "3" * 64, "execution_decision_hash": "4" * 64},
        ]),
    ],
)
def test_changing_any_section_changes_packet_hash(section: str, mutation: list) -> None:
    base = _base_kwargs()
    p1 = build_evidence_packet_v2(**base)
    mutated = dict(base)
    mutated[section] = mutation
    p2 = build_evidence_packet_v2(**mutated)
    assert p1["evidence_packet_hash"] != p2["evidence_packet_hash"], (
        f"mutating {section} must change evidence_packet_hash (otherwise that section is not hashed)"
    )


def test_changing_contract_surface_sha256_changes_packet_hash() -> None:
    base = _base_kwargs()
    p1 = build_evidence_packet_v2(**base)
    mutated = dict(base)
    mutated["contract_surface_sha256"] = "f" * 64
    p2 = build_evidence_packet_v2(**mutated)
    assert p1["evidence_packet_hash"] != p2["evidence_packet_hash"]


def test_changing_context_bundle_hash_changes_packet_hash() -> None:
    base = _base_kwargs()
    p1 = build_evidence_packet_v2(**base)
    mutated = dict(base)
    mutated["context_bundle_hash"] = "f" * 64
    p2 = build_evidence_packet_v2(**mutated)
    assert p1["evidence_packet_hash"] != p2["evidence_packet_hash"]


def test_changing_source_repo_changes_packet_hash() -> None:
    base = _base_kwargs()
    p1 = build_evidence_packet_v2(**base)
    p2 = build_evidence_packet_v2(**base, source_repo="LawFirm-os-some-other-repo")
    # source_repo default is "LawFirm-os-orchestrator"; override should change the hash.
    assert p1["evidence_packet_hash"] != p2["evidence_packet_hash"]
