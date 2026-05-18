"""ContextBundle compiler (PR-03).

Builds a deterministic ContextBundle, enforces required fields fail-closed,
and binds the bundle to the substrate authority surface via contracts.lock.json.
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Sequence

from lawfirm_os_orchestrator.domain.context_bundle import (
    ContextBudget,
    ContextBundle,
    ContextBundleTask,
    PolicyRefStub,
    SourceRefStub,
    ToolRefStub,
    SCHEMA_VERSION,
    context_bundle_hash,
)
from lawfirm_os_orchestrator.substrate.contract_lock import (
    DEFAULT_CONTRACT_LOCK_PATH,
    load_contract_lock,
)


class ContextCompilerError(ValueError):
    """Raised when ContextBundle compilation cannot proceed (fail-closed)."""


def _iso_utc_now() -> str:
    return datetime.now(tz=UTC).isoformat().replace("+00:00", "Z")


def compile_context_bundle(
    *,
    context_bundle_id: str,
    run_id: str,
    task: ContextBundleTask,
    source_refs: Sequence[SourceRefStub],
    policy_refs: Sequence[PolicyRefStub],
    tool_refs: Sequence[ToolRefStub] = (),
    context_budget: ContextBudget,
    contract_lock_path: Path | None = None,
    generated_at: str | None = None,
) -> ContextBundle:
    """Compile a ContextBundle. Required fields are enforced fail-closed.

    The bundle's contract_surface_sha256 and substrate_repo_commit_sha are
    pulled from the orchestrator's contracts.lock.json. A bundle is only
    valid under a single substrate authority surface.
    """
    if not context_bundle_id:
        raise ContextCompilerError("context_bundle_id required")
    if not run_id:
        raise ContextCompilerError("run_id required")
    if not task or not task.task_id or not task.task_kind or not task.task_description_hash:
        raise ContextCompilerError("task with task_id, task_kind, task_description_hash required")
    if not source_refs:
        raise ContextCompilerError("at least one source_ref required (no implicit RAG fallback)")
    if not policy_refs:
        raise ContextCompilerError("at least one policy_ref required (no implicit policy)")
    if context_budget is None or context_budget.max_input_bytes <= 0 or context_budget.max_steps <= 0:
        raise ContextCompilerError("context_budget with positive max_input_bytes and max_steps required")

    lock = load_contract_lock(contract_lock_path or DEFAULT_CONTRACT_LOCK_PATH)
    if not lock.contract_surface_sha256:
        raise ContextCompilerError(
            "contracts.lock.json has no contract_surface_lock.surface_sha256; "
            "ContextBundle compilation requires an active contract surface pin"
        )
    if not lock.substrate_repo_commit_sha:
        raise ContextCompilerError("contracts.lock.json has no substrate_repo_commit_sha")

    src_tuple = tuple(source_refs)
    policy_tuple = tuple(policy_refs)
    tool_tuple = tuple(tool_refs)

    payload_for_hash: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "context_bundle_id": context_bundle_id,
        "contract_surface_sha256": lock.contract_surface_sha256,
        "substrate_repo_commit_sha": lock.substrate_repo_commit_sha,
        "generated_at": generated_at or _iso_utc_now(),
        "run_id": run_id,
        "task": asdict(task),
        "source_refs": [asdict(s) for s in src_tuple],
        "policy_refs": [_compact(asdict(p)) for p in policy_tuple],
        "tool_refs": [_compact(asdict(t)) for t in tool_tuple],
        "context_budget": _compact(asdict(context_budget)),
    }
    digest = context_bundle_hash(payload_for_hash)

    return ContextBundle(
        schema_version=SCHEMA_VERSION,
        context_bundle_id=context_bundle_id,
        contract_surface_sha256=lock.contract_surface_sha256,
        substrate_repo_commit_sha=lock.substrate_repo_commit_sha,
        generated_at=payload_for_hash["generated_at"],
        run_id=run_id,
        task=task,
        source_refs=src_tuple,
        policy_refs=policy_tuple,
        tool_refs=tool_tuple,
        context_budget=context_budget,
        context_bundle_hash=digest,
    )


def _compact(d: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in d.items() if v is not None}
