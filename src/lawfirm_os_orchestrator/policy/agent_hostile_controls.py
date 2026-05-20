from __future__ import annotations

from datetime import UTC, datetime, timedelta
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lawfirm_os_orchestrator.domain.agent_controls import (
    AgentIdentity,
    AuthzDecision,
    PolicyDenied,
    PromptVersionRef,
    RevocationState,
    ToolAuthoritySpec,
)
from lawfirm_os_orchestrator.domain.models import SyntheticExceptionInput
from lawfirm_os_orchestrator.substrate.reader import SubstrateSnapshot
from lawfirm_os_orchestrator.util.hashing import sha256_file, sha256_json
from lawfirm_os_orchestrator.util.ids import new_id
from lawfirm_os_orchestrator.util.json_io import read_json
from lawfirm_os_orchestrator.util.time import utc_now


DEFAULT_AGENT_HOSTILE_CONFIG = Path("config") / "agent_hostile"
DEFAULT_PROMPT_REGISTRY = DEFAULT_AGENT_HOSTILE_CONFIG / "prompt_registry.json"
DEFAULT_REVOCATION_REGISTRY = DEFAULT_AGENT_HOSTILE_CONFIG / "revocation_registry.json"
DEFAULT_TOOL_AUTHORITY_MANIFEST = DEFAULT_AGENT_HOSTILE_CONFIG / "tool_authority_manifest.json"
DEFAULT_CLASSIFIER_TOOL_ID = "orchestrator.tool.synthetic_classify_exception.v1"
DEFAULT_CLASSIFY_PROMPT_REF = "orchestrator.prompt.classify_exception.synthetic.v1"
DEFAULT_AGENT_CONTROL_SOURCE = "substrate"
DEFAULT_CLASSIFY_PROMPT_FILE = Path("prompts") / "runtime" / "classify_exception_system.txt"
SUBSTRATE_PROMPT_REGISTRY = Path("registry") / "prompt-registry.json"
SUBSTRATE_TOOL_AUTHORITY_REGISTRY = Path("registry") / "tool-authority-registry.json"
SUBSTRATE_ENDPOINT_AUTHORITY_REGISTRY = Path("registry") / "endpoint-authority-registry.json"
SUBSTRATE_CONTROL_REGISTRY = Path("registry") / "agent-hostile-control-registry.json"
SUBSTRATE_CONTRACT_EXPORT = Path("registry") / "agent-control-contract-export.json"
DEFAULT_TENANT_ID = "tenant.synthetic"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _default_substrate_root() -> Path:
    return _repo_root().parent / "LawFirm-os-semantic-substrate"


def _utc_dt() -> datetime:
    return datetime.now(tz=UTC)


def _resolve(path: str | Path, *, base: Path | None = None) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return (base or _repo_root()) / candidate


def _scope_hash(scope: dict[str, Any]) -> str:
    return sha256_json(scope)


@dataclass(frozen=True)
class AgentControlRegistrySource:
    source: str
    prompt_registry_path: Path
    tool_registry_path: Path
    endpoint_registry_path: Path | None = None
    control_registry_path: Path | None = None
    contract_export_path: Path | None = None
    revocation_registry_path: Path | None = None

    def provenance(self, *, contract_sha: str) -> dict[str, Any]:
        registries: dict[str, dict[str, Any]] = {}
        for name, path in (
            ("prompt", self.prompt_registry_path),
            ("tool_authority", self.tool_registry_path),
            ("endpoint_authority", self.endpoint_registry_path),
            ("agent_hostile_control", self.control_registry_path),
            ("agent_control_contract_export", self.contract_export_path),
            ("runtime_revocation_state", self.revocation_registry_path),
        ):
            if path is None:
                continue
            registries[name] = {
                "registry_path": str(path),
                "registry_hash": sha256_file(path) if path.is_file() else None,
            }
        primary = registries["prompt"]
        return {
            "source": self.source,
            "canonical": self.source == "substrate",
            "fixture_only": self.source == "local_fixture",
            "registry_path": primary["registry_path"],
            "registry_hash": primary["registry_hash"],
            "contract_sha": contract_sha,
            "registries": registries,
        }


def resolve_agent_control_registry_source(
    *,
    source: str | None = None,
    substrate_root: str | Path | None = None,
    prompt_registry: str | Path | None = None,
    tool_manifest: str | Path | None = None,
    revocation_registry: str | Path | None = None,
) -> AgentControlRegistrySource:
    selected = source or DEFAULT_AGENT_CONTROL_SOURCE
    if selected == "local-fixture":
        selected = "local_fixture"
    if selected not in {"substrate", "local_fixture"}:
        raise ValueError(f"unknown agent control source: {selected}")

    if selected == "local_fixture":
        return AgentControlRegistrySource(
            source="local_fixture",
            prompt_registry_path=_resolve(prompt_registry or DEFAULT_PROMPT_REGISTRY),
            tool_registry_path=_resolve(tool_manifest or DEFAULT_TOOL_AUTHORITY_MANIFEST),
            revocation_registry_path=_resolve(revocation_registry or DEFAULT_REVOCATION_REGISTRY),
        )

    root = _resolve(substrate_root or _default_substrate_root())
    paths = {
        "prompt_registry": root / SUBSTRATE_PROMPT_REGISTRY,
        "tool_registry": root / SUBSTRATE_TOOL_AUTHORITY_REGISTRY,
        "endpoint_registry": root / SUBSTRATE_ENDPOINT_AUTHORITY_REGISTRY,
        "control_registry": root / SUBSTRATE_CONTROL_REGISTRY,
        "contract_export": root / SUBSTRATE_CONTRACT_EXPORT,
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing canonical Semantic Substrate agent-control registries: "
            + ", ".join(missing)
        )
    return AgentControlRegistrySource(
        source="substrate",
        prompt_registry_path=paths["prompt_registry"],
        tool_registry_path=paths["tool_registry"],
        endpoint_registry_path=paths["endpoint_registry"],
        control_registry_path=paths["control_registry"],
        contract_export_path=paths["contract_export"],
        revocation_registry_path=_resolve(revocation_registry) if revocation_registry else None,
    )


def make_decision(
    *,
    run_id: str,
    gate: str,
    result: str,
    reason_code: str,
    actor_id: str,
    scope: dict[str, Any],
    policy_ref: str,
    evidence_ref: str | None = None,
) -> AuthzDecision:
    return AuthzDecision(
        decision_id=new_id("authz"),
        run_id=run_id,
        gate=gate,
        result=result,
        reason_code=reason_code,
        actor_id=actor_id,
        scope_hash=_scope_hash(scope),
        evaluated_at=utc_now(),
        policy_ref=policy_ref,
        evidence_ref=evidence_ref,
        details=scope,
    )


def enforce(decision: AuthzDecision) -> AuthzDecision:
    if decision.result == "deny":
        raise PolicyDenied(decision)
    return decision


def build_agent_identity(
    *,
    run_id: str,
    event: SyntheticExceptionInput,
    snapshot: SubstrateSnapshot,
    agent_id: str | None = None,
    delegating_user_id: str | None = None,
    tenant_id: str | None = None,
    tool_id: str = DEFAULT_CLASSIFIER_TOOL_ID,
) -> AgentIdentity:
    issued_at = _utc_dt()
    return AgentIdentity(
        agent_instance_id=agent_id or f"agent:{run_id}",
        delegating_user_id=delegating_user_id,
        tenant_id=tenant_id or DEFAULT_TENANT_ID,
        matter_scope=(),
        route_scope=tuple(snapshot.allowed_route_ids),
        tool_scope=(tool_id,),
        data_scope=("synthetic_exception_input",),
        issued_at=issued_at,
        expires_at=issued_at + timedelta(hours=1),
    )


def agent_identity_gate(run_id: str, actor: AgentIdentity) -> AuthzDecision:
    blocked = not (
        actor.actor_type == "agent"
        and actor.agent_instance_id
        and actor.tenant_id
        and actor.route_scope
        and actor.tool_scope
        and actor.data_scope
    )
    return enforce(
        make_decision(
            run_id=run_id,
            gate="AgentIdentityGate",
            result="deny" if blocked else "pass",
            reason_code="agent_identity_invalid" if blocked else "agent_identity_ok",
            actor_id=actor.agent_instance_id,
            scope=actor.model_dump(mode="json"),
            policy_ref="orchestrator.agent_identity.v1",
        )
    )


def load_revocation_state(path: str | Path | None, actor: AgentIdentity) -> RevocationState:
    if path is None:
        return RevocationState(agent_instance_id=actor.agent_instance_id)
    registry_path = _resolve(path)
    if not registry_path.is_file():
        return RevocationState(
            agent_instance_id=actor.agent_instance_id,
            revoked=True,
            reason="revocation_registry_unavailable",
        )
    registry = read_json(registry_path)
    agent_record = registry.get("revoked_agents", {}).get(actor.agent_instance_id)
    global_routes = tuple(registry.get("paused_routes", []))
    global_tools = tuple(registry.get("denied_tools", []))
    if agent_record:
        return RevocationState.model_validate(
            {
                **agent_record,
                "agent_instance_id": actor.agent_instance_id,
                "blocked_routes": tuple(agent_record.get("blocked_routes", ())) + global_routes,
                "blocked_tools": tuple(agent_record.get("blocked_tools", ())) + global_tools,
            }
        )
    return RevocationState(
        agent_instance_id=actor.agent_instance_id,
        blocked_routes=global_routes,
        blocked_tools=global_tools,
    )


def revocation_gate(
    *,
    run_id: str,
    actor: AgentIdentity,
    state: RevocationState,
    route_id: str | None,
    tool_id: str,
    evidence_ref: str | None = None,
) -> AuthzDecision:
    reason = "revocation_ok"
    blocked = False
    if state.revoked:
        blocked = True
        reason = state.reason or "agent_revoked"
    elif route_id and route_id in state.blocked_routes:
        blocked = True
        reason = "route_paused"
    elif tool_id in state.blocked_tools:
        blocked = True
        reason = "tool_denied"
    return enforce(
        make_decision(
            run_id=run_id,
            gate="RevocationGate",
            result="deny" if blocked else "pass",
            reason_code=reason,
            actor_id=actor.agent_instance_id,
            scope={
                "revocation_state": state.model_dump(mode="json"),
                "route_id": route_id,
                "tool_id": tool_id,
            },
            policy_ref="orchestrator.revocation.v1",
            evidence_ref=evidence_ref,
        )
    )


def _normalize_tool_record(record: dict[str, Any]) -> dict[str, Any]:
    approval_policy = record.get("approval_policy") or {}
    return {
        "tool_id": record["tool_id"],
        "version": record.get("version", "1.0.0"),
        "risk_class": record["risk_class"],
        "input_schema_ref": record.get("input_schema_ref") or "schema:none",
        "output_schema_ref": record.get("output_schema_ref") or "schema:none",
        "allowed_actor_types": record.get("allowed_actor_types", ()),
        "auth_required": record.get("auth_required", False),
        "agent_identity_required": record.get("agent_identity_required", False),
        "audit_event_required": record.get("audit_event_required", False),
        "approval_required": record.get("approval_required", approval_policy.get("approval_required", True)),
        "idempotency_required": record.get("idempotency_required", False),
        "data_domains": record.get("data_domains", record.get("allowed_data_classes", ())),
        "timeout_seconds": record.get("timeout_seconds", 30),
        "retry_policy_ref": record.get("retry_policy_ref", "retry.policy.unspecified"),
    }


def load_tool_authority_manifest(path: str | Path) -> tuple[ToolAuthoritySpec, ...]:
    manifest_path = _resolve(path)
    raw = read_json(manifest_path)
    return tuple(
        ToolAuthoritySpec.model_validate(_normalize_tool_record(item))
        for item in raw.get("tools", [])
        if item.get("status") != "draft_metadata_only"
    )


def validate_tool_authority_manifest(path: str | Path) -> tuple[ToolAuthoritySpec, ...]:
    specs = load_tool_authority_manifest(path)
    for spec in specs:
        if not spec.auth_required:
            raise ValueError(f"tool {spec.tool_id} has auth_required=false")
        if "agent" in spec.allowed_actor_types and not spec.agent_identity_required:
            raise ValueError(f"tool {spec.tool_id} has agent_identity_required=false")
        if not spec.audit_event_required:
            raise ValueError(f"tool {spec.tool_id} has audit_event_required=false")
        if spec.risk_class in {"write", "execute"} and not spec.approval_required:
            raise ValueError(f"tool {spec.tool_id} side-effecting risk class lacks approval policy")
    return specs


def tool_authority_gate(
    *,
    run_id: str,
    actor: AgentIdentity,
    tool_manifest_path: str | Path,
    tool_id: str,
) -> AuthzDecision:
    manifest_path = _resolve(tool_manifest_path)
    try:
        tools = validate_tool_authority_manifest(manifest_path)
    except Exception as exc:
        return enforce(
            make_decision(
                run_id=run_id,
                gate="ToolAuthorityGate",
                result="deny",
                reason_code="tool_manifest_invalid",
                actor_id=actor.agent_instance_id,
                scope={"tool_id": tool_id, "error": str(exc), "manifest_path": str(manifest_path)},
                policy_ref="orchestrator.tool_authority.v1",
                evidence_ref=str(manifest_path),
            )
        )
    tool = next((spec for spec in tools if spec.tool_id == tool_id), None)
    reason = "tool_authority_ok"
    blocked = False
    if tool is None:
        blocked = True
        reason = "unknown_tool"
    elif tool_id not in actor.tool_scope:
        blocked = True
        reason = "tool_outside_agent_scope"
    elif "agent" not in tool.allowed_actor_types:
        blocked = True
        reason = "agent_actor_not_allowed"
    elif tool.risk_class in {"write", "execute"} and not tool.approval_required:
        blocked = True
        reason = "side_effecting_tool_missing_approval"
    return enforce(
        make_decision(
            run_id=run_id,
            gate="ToolAuthorityGate",
            result="deny" if blocked else "pass",
            reason_code=reason,
            actor_id=actor.agent_instance_id,
            scope={
                "tool_id": tool_id,
                "actor_tool_scope": actor.tool_scope,
                "manifest_path": str(manifest_path),
                "tool": tool.model_dump(mode="json") if tool else None,
            },
            policy_ref="orchestrator.tool_authority.v1",
            evidence_ref=str(manifest_path),
        )
    )


def load_prompt_version(
    *,
    registry_path: str | Path,
    prompt_ref: str,
) -> PromptVersionRef | None:
    registry = read_json(_resolve(registry_path))
    record = next((p for p in registry.get("prompts", []) if p.get("prompt_ref") == prompt_ref), None)
    if record is None:
        return None
    normalized = {
        "prompt_ref": record["prompt_ref"],
        "prompt_version": record["prompt_version"],
        "prompt_sha256": record["prompt_sha256"],
        "approved": record.get("approved", record.get("prompt_approved", False)),
        "approved_by": record.get("approved_by"),
        "approved_at": record.get("approved_at"),
        "policy_bundle_id": record.get("policy_bundle_id"),
        "prompt_file": record.get("prompt_file") or str(DEFAULT_CLASSIFY_PROMPT_FILE),
    }
    return PromptVersionRef.model_validate(normalized)


def prompt_integrity_gate(
    *,
    run_id: str,
    actor: AgentIdentity,
    prompt_registry_path: str | Path,
    prompt_ref: str,
) -> tuple[AuthzDecision, PromptVersionRef | None]:
    registry_path = _resolve(prompt_registry_path)
    prompt = load_prompt_version(registry_path=registry_path, prompt_ref=prompt_ref)
    reason = "prompt_integrity_ok"
    blocked = False
    actual_hash = None
    if prompt is None:
        blocked = True
        reason = "prompt_not_registered"
    else:
        prompt_file = _resolve(prompt.prompt_file)
        if not prompt_file.is_file():
            blocked = True
            reason = "prompt_file_missing"
        else:
            actual_hash = sha256_file(prompt_file)
            if actual_hash != prompt.prompt_sha256:
                blocked = True
                reason = "prompt_hash_mismatch"
            elif not prompt.approved:
                blocked = True
                reason = "prompt_not_approved"
            elif not prompt.policy_bundle_id:
                blocked = True
                reason = "prompt_policy_bundle_missing"
    decision = make_decision(
        run_id=run_id,
        gate="PromptIntegrityGate",
        result="deny" if blocked else "pass",
        reason_code=reason,
        actor_id=actor.agent_instance_id,
        scope={
            "prompt_ref": prompt_ref,
            "registered_prompt": prompt.model_dump(mode="json") if prompt else None,
            "actual_prompt_sha256": actual_hash,
        },
        policy_ref="orchestrator.prompt_integrity.v1",
        evidence_ref=str(registry_path),
    )
    enforce(decision)
    return decision, prompt


def blast_radius_from_actor(actor: AgentIdentity) -> dict[str, Any]:
    return {
        "tenant_id": actor.tenant_id,
        "matter_scope": list(actor.matter_scope),
        "route_scope": list(actor.route_scope),
        "tool_scope": list(actor.tool_scope),
        "data_scope": list(actor.data_scope),
        "write_scope": [],
    }


def revocation_snapshot(state: RevocationState, *, route_id: str | None, tool_id: str) -> dict[str, Any]:
    return {
        "checked_at": utc_now(),
        "agent_instance_id": state.agent_instance_id,
        "agent_revoked": state.revoked,
        "route_revoked": bool(route_id and route_id in state.blocked_routes),
        "tool_revoked": tool_id in state.blocked_tools,
        "reason": state.reason,
        "blocked_routes": list(state.blocked_routes),
        "blocked_tools": list(state.blocked_tools),
    }


def prompt_integrity_proof(prompt: PromptVersionRef | None) -> dict[str, Any]:
    if prompt is None:
        return {
            "prompt_ref": None,
            "prompt_version": None,
            "prompt_sha256": None,
            "approved": False,
            "policy_bundle_id": None,
        }
    return {
        "prompt_ref": prompt.prompt_ref,
        "prompt_version": prompt.prompt_version,
        "prompt_sha256": prompt.prompt_sha256,
        "approved": prompt.approved,
        "approved_by": prompt.approved_by,
        "approved_at": prompt.approved_at.isoformat() if prompt.approved_at else None,
        "policy_bundle_id": prompt.policy_bundle_id,
    }
