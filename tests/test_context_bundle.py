"""Tests for the PR-03 orchestrator ContextBundle compiler."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from lawfirm_os_orchestrator.context.compiler import (
    ContextCompilerError,
    compile_context_bundle,
)
from lawfirm_os_orchestrator.domain.context_bundle import (
    ContextBudget,
    ContextBundleTask,
    PolicyRefStub,
    SourceRefStub,
    context_bundle_hash,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOCK = REPO_ROOT / "contracts.lock.json"
FIXED_AT = "2026-05-18T00:00:00Z"


def _minimal_inputs():
    return dict(
        context_bundle_id="ctx-1",
        run_id="run-1",
        task=ContextBundleTask(
            task_id="task-1",
            task_kind="synthetic_read_only",
            task_description_hash="a" * 64,
        ),
        source_refs=[
            SourceRefStub(source_ref_id="sref-1", source_id="src-1", content_hash="b" * 64),
        ],
        policy_refs=[PolicyRefStub(policy_ref_id="pref-1", policy_id="policy-1")],
        tool_refs=[],
        context_budget=ContextBudget(max_input_bytes=1024, max_steps=4),
        generated_at=FIXED_AT,
    )


def test_compile_context_bundle_emits_64char_hex_hash() -> None:
    bundle = compile_context_bundle(**_minimal_inputs())
    assert len(bundle.context_bundle_hash) == 64
    assert all(c in "0123456789abcdef" for c in bundle.context_bundle_hash)


def test_compile_context_bundle_binds_to_substrate_surface() -> None:
    bundle = compile_context_bundle(**_minimal_inputs())
    lock = json.loads(DEFAULT_LOCK.read_text(encoding="utf-8"))
    assert bundle.contract_surface_sha256 == lock["contract_surface_lock"]["surface_sha256"]
    assert bundle.substrate_repo_commit_sha == lock["substrate_repo_commit_sha"]


def test_context_bundle_hash_is_field_order_independent() -> None:
    a = {"b": 1, "a": [3, 2, 1]}
    b = {"a": [3, 2, 1], "b": 1}
    assert context_bundle_hash(a) == context_bundle_hash(b)


def test_context_bundle_hash_excludes_itself() -> None:
    inputs = _minimal_inputs()
    b1 = compile_context_bundle(**inputs)
    b2 = compile_context_bundle(**inputs)
    assert b1.context_bundle_hash == b2.context_bundle_hash, "identical inputs => identical hash"


def test_changing_source_refs_changes_hash() -> None:
    inputs = _minimal_inputs()
    b1 = compile_context_bundle(**inputs)
    inputs["source_refs"] = [
        SourceRefStub(source_ref_id="sref-2", source_id="src-2", content_hash="c" * 64),
    ]
    b2 = compile_context_bundle(**inputs)
    assert b1.context_bundle_hash != b2.context_bundle_hash


def test_missing_source_refs_fails_closed() -> None:
    inputs = _minimal_inputs()
    inputs["source_refs"] = []
    with pytest.raises(ContextCompilerError, match="source_ref"):
        compile_context_bundle(**inputs)


def test_missing_policy_refs_fails_closed() -> None:
    inputs = _minimal_inputs()
    inputs["policy_refs"] = []
    with pytest.raises(ContextCompilerError, match="policy_ref"):
        compile_context_bundle(**inputs)


def test_missing_run_id_fails_closed() -> None:
    inputs = _minimal_inputs()
    inputs["run_id"] = ""
    with pytest.raises(ContextCompilerError):
        compile_context_bundle(**inputs)


def test_missing_context_bundle_id_fails_closed() -> None:
    inputs = _minimal_inputs()
    inputs["context_bundle_id"] = ""
    with pytest.raises(ContextCompilerError):
        compile_context_bundle(**inputs)


def test_invalid_context_budget_fails_closed() -> None:
    inputs = _minimal_inputs()
    inputs["context_budget"] = ContextBudget(max_input_bytes=0, max_steps=0)
    with pytest.raises(ContextCompilerError, match="context_budget"):
        compile_context_bundle(**inputs)


def test_missing_task_fields_fails_closed() -> None:
    inputs = _minimal_inputs()
    inputs["task"] = ContextBundleTask(task_id="", task_kind="x", task_description_hash="a" * 64)
    with pytest.raises(ContextCompilerError, match="task"):
        compile_context_bundle(**inputs)


def test_compiled_bundle_to_payload_round_trip() -> None:
    bundle = compile_context_bundle(**_minimal_inputs())
    payload = bundle.to_payload()
    assert payload["context_bundle_hash"] == bundle.context_bundle_hash
    assert payload["contract_surface_sha256"] == bundle.contract_surface_sha256
    assert payload["source_refs"][0]["source_ref_id"] == "sref-1"
    # Recomputing hash from the payload (excluding the field) must equal the stored hash.
    assert context_bundle_hash(payload) == bundle.context_bundle_hash
