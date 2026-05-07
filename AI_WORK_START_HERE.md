# AI Work Start Here

Canonical machine name: `LawFirm-os-orchestrator`. Plane: execution.
Sibling repos: `LawFirm-os-semantic-substrate` (control plane), `exceptions-lake-runtime-main` (evidence plane).
For authority order across repos, read the substrate's `governance/CROSS_REPO_MAP.md`.

Route: `orchestrator.mvp.classify_exception`
Mode: `synthetic_only_local_first`
V1 seed read-first doc: `docs/seed/00_CODEX_READ_FIRST.md`
Cross-repo route mapping: `docs/CANONICAL_ROUTE_MAPPING.md`
Allowed paths: `src/lawfirm_os_orchestrator/**`, `tests/**`, `examples/**`, `docs/**`, `config/**`, `contracts.lock.json`
Forbidden paths: Semantic Substrate and Exceptions Lake runtime repos except through documented patches.
Contract surfaces touched (read-only): canonical orchestrator manifest at substrate `manifests/contract_manifest.v1.json`, `registry/exception-route-registry.json`, `registry/orchestrator-contract-export.json`, governance boundary docs.
Loading discipline: manifest-first; required manifest fields (`manifest_id`, `manifest_version`, `policy_bundle_id`, `canonical_schema_keys`, `registry_refs`) must not be silently defaulted. Fail-closed on SHA drift or missing required fields.
Validation plan: run `python -m pytest` and CLI smoke test.
Stop conditions: see `docs/decisions/synthetic_only_policy.md`.
