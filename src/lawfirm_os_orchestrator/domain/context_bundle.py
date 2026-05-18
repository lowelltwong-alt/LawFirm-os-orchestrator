"""ContextBundle domain model and canonical hashing (PR-03).

A ContextBundle is the deterministic, governed working context handed to a
bounded runtime action. It carries refs and hashes only; never raw privileged
payloads. Its canonical hash binds the consumer to the substrate authority
surface (contract_surface_sha256) it was produced under.

Substrate schema: schemas/context-bundle.schema.json (context-bundle-v1).
"""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any

from lawfirm_os_orchestrator.util.hashing import canonical_json


SCHEMA_VERSION = "context_bundle.v1"


@dataclass(frozen=True)
class SourceRefStub:
    source_ref_id: str
    source_id: str
    content_hash: str


@dataclass(frozen=True)
class PolicyRefStub:
    policy_ref_id: str
    policy_id: str
    policy_version: str | None = None


@dataclass(frozen=True)
class ToolRefStub:
    tool_ref_id: str
    tool_id: str
    tool_version: str | None = None


@dataclass(frozen=True)
class ContextBudget:
    max_input_bytes: int
    max_steps: int
    max_tool_calls: int | None = None


@dataclass(frozen=True)
class ContextBundleTask:
    task_id: str
    task_kind: str
    task_description_hash: str


@dataclass(frozen=True)
class ContextBundle:
    schema_version: str
    context_bundle_id: str
    contract_surface_sha256: str
    substrate_repo_commit_sha: str
    generated_at: str
    run_id: str
    task: ContextBundleTask
    source_refs: tuple[SourceRefStub, ...]
    policy_refs: tuple[PolicyRefStub, ...]
    tool_refs: tuple[ToolRefStub, ...]
    context_budget: ContextBudget
    context_bundle_hash: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "context_bundle_id": self.context_bundle_id,
            "context_bundle_hash": self.context_bundle_hash,
            "contract_surface_sha256": self.contract_surface_sha256,
            "substrate_repo_commit_sha": self.substrate_repo_commit_sha,
            "generated_at": self.generated_at,
            "run_id": self.run_id,
            "task": asdict(self.task),
            "source_refs": [asdict(s) for s in self.source_refs],
            "policy_refs": [_compact(asdict(p)) for p in self.policy_refs],
            "tool_refs": [_compact(asdict(t)) for t in self.tool_refs],
            "context_budget": _compact(asdict(self.context_budget)),
        }


def _compact(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}


def context_bundle_hash(payload: dict[str, Any]) -> str:
    """Bare-hex SHA-256 of the canonical JSON payload with the context_bundle_hash
    field excluded. Field-order independent (canonical_json sorts keys)."""
    clean = {k: v for k, v in payload.items() if k != "context_bundle_hash"}
    return hashlib.sha256(canonical_json(clean)).hexdigest()
