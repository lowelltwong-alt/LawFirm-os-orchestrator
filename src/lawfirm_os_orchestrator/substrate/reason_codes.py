"""Substrate-owned controlled vocabulary, loaded fail-closed (PR-05.5).

Single source of truth: the orchestrator does not invent reason_code or
semantic-mutation-action values. They are read from the substrate's
``registry/runtime-reason-codes-registry.json`` at import time.

If the substrate is not available or the registry is malformed, this module
raises at import. That is the desired behavior: the orchestrator must not
run under an unknown controlled vocabulary.

Discovery order for substrate location:

1. ``LFOS_SUBSTRATE_PATH`` environment variable, if set.
2. ``<orchestrator-repo>/../<contract_repo>`` derived from this repo's
   ``contracts.lock.json``.
3. ``<orchestrator-repo>/../LawFirm-os-semantic-substrate`` as a final fallback.

No silent hardcoded fallback list. No "invent if substrate unavailable" path.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Mapping

_REPO_ROOT = Path(__file__).resolve().parents[3]
_LOCK_PATH = _REPO_ROOT / "contracts.lock.json"


class ReasonCodeRegistryError(RuntimeError):
    """Raised when the substrate controlled-vocabulary registry cannot be loaded."""


def _resolve_substrate_root() -> Path:
    override = os.environ.get("LFOS_SUBSTRATE_PATH")
    if override:
        candidate = Path(override)
        if candidate.is_dir():
            return candidate
        raise ReasonCodeRegistryError(
            f"LFOS_SUBSTRATE_PATH points to a non-directory: {override}"
        )
    if _LOCK_PATH.is_file():
        try:
            lock = json.loads(_LOCK_PATH.read_text(encoding="utf-8"))
            contract_repo = lock.get("contract_repo")
        except (json.JSONDecodeError, OSError) as exc:
            raise ReasonCodeRegistryError(
                f"cannot read orchestrator contracts.lock.json at {_LOCK_PATH}: {exc}"
            ) from exc
        if isinstance(contract_repo, str) and contract_repo:
            candidate = _REPO_ROOT.parent / contract_repo
            if candidate.is_dir():
                return candidate
    fallback = _REPO_ROOT.parent / "LawFirm-os-semantic-substrate"
    if fallback.is_dir():
        return fallback
    raise ReasonCodeRegistryError(
        "substrate repo not discoverable; set LFOS_SUBSTRATE_PATH or place the "
        "substrate as a sibling of the orchestrator repo"
    )


def _load_vocabularies(substrate_root: Path) -> Mapping[str, frozenset[str]]:
    registry_path = substrate_root / "registry" / "runtime-reason-codes-registry.json"
    if not registry_path.is_file():
        raise ReasonCodeRegistryError(
            f"runtime-reason-codes-registry.json not found at {registry_path}; "
            "orchestrator cannot operate without the substrate controlled vocabulary"
        )
    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ReasonCodeRegistryError(
            f"runtime-reason-codes-registry.json is not valid JSON: {exc}"
        ) from exc
    vocabs = raw.get("vocabularies")
    if not isinstance(vocabs, dict):
        raise ReasonCodeRegistryError(
            "runtime-reason-codes-registry.json is missing a 'vocabularies' object"
        )
    result: dict[str, frozenset[str]] = {}
    for name, body in vocabs.items():
        values = body.get("values") if isinstance(body, dict) else None
        if not isinstance(values, list) or not all(isinstance(v, str) for v in values):
            raise ReasonCodeRegistryError(
                f"vocabulary {name!r} is missing a list of string values"
            )
        result[name] = frozenset(values)
    return result


_VOCABS = _load_vocabularies(_resolve_substrate_root())


def _require(vocab: str, value: str) -> str:
    allowed = _VOCABS.get(vocab, frozenset())
    if value not in allowed:
        raise ReasonCodeRegistryError(
            f"{value!r} is not registered in vocabulary {vocab!r}"
        )
    return value


# ---------- ExecutionDecision.reason_code constants ----------

_REASON = "execution_decision.reason_codes"

ALLOWED_UNDER_AUTHORITY_POLICY = _require(_REASON, "allowed_under_authority_policy")
UNKNOWN_TOOL = _require(_REASON, "unknown_tool")
UNKNOWN_ROUTE = _require(_REASON, "unknown_route")
UNKNOWN_EVENT_CLASS = _require(_REASON, "unknown_event_class")
SEMANTIC_MUTATION_FORBIDDEN = _require(_REASON, "semantic_mutation_forbidden")
EXTERNAL_WRITES_FORBIDDEN_IN_MVP = _require(_REASON, "external_writes_forbidden_in_mvp")
WRITE_REQUIRES_HUMAN_APPROVAL = _require(_REASON, "write_requires_human_approval")
WRITE_REQUIRES_EXPLICIT_APPROVAL_POLICY = _require(_REASON, "write_requires_explicit_approval_policy")

EXECUTION_DECISION_REASON_CODES: frozenset[str] = _VOCABS[_REASON]


# ---------- runtime.semantic_mutation_actions deny-list ----------

SEMANTIC_MUTATION_ACTIONS: frozenset[str] = _VOCABS["runtime.semantic_mutation_actions"]


# ---------- helpers ----------

def is_registered_reason_code(value: str) -> bool:
    return value in EXECUTION_DECISION_REASON_CODES


def is_semantic_mutation_action(value: str) -> bool:
    return value in SEMANTIC_MUTATION_ACTIONS
