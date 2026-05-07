# AI Work Start Here

Canonical machine name: `LawFirm-os-orchestrator`. Plane: execution.
Sibling repos: `LawFirm-os-semantic-substrate` (control plane), `exceptions-lake-runtime-main` (evidence plane).
For authority order across repos, read the substrate's `governance/CROSS_REPO_MAP.md`.

Route: `orchestrator.mvp.classify_exception`
Mode: `synthetic_only_local_first`
PR02/PR03/PR04 local routes: `classify-autonomy`, `select-harness`, `watch-green-lanes`, `generate-codex-task`
V1 seed read-first doc: `docs/seed/00_CODEX_READ_FIRST.md`
Cross-repo route mapping: `docs/CANONICAL_ROUTE_MAPPING.md`
Allowed paths: `src/lawfirm_os_orchestrator/**`, `tests/**`, `examples/**`, `docs/**`, `config/**`, `contracts.lock.json`
Forbidden paths: Semantic Substrate and Exceptions Lake runtime repos except through documented patches.
Contract surfaces touched (read-only): canonical orchestrator manifest at substrate `manifests/contract_manifest.v1.json`, `registry/exception-route-registry.json`, `registry/orchestrator-contract-export.json`, governance boundary docs.
Loading discipline: manifest-first; required manifest fields (`manifest_id`, `manifest_version`, `policy_bundle_id`, `canonical_schema_keys`, `registry_refs`) must not be silently defaulted. Fail-closed on SHA drift or missing required fields.
Autonomy discipline: risk color controls authority; hardness controls harness depth; leverage controls priority; stakes modeling remains PR07.
Green-lane discipline: green lanes are conditional; signals may downgrade green to yellow/red; humans restore green authority.
Task-packet discipline: Codex task packets are inert build instructions only and must not execute tools, code, Git, models, network, Substrate writes, or Lake writes.
Validation plan: run `python -m pytest`, `python scripts/check_safety.py --stdout json`, evals, and CLI smoke tests.
Stop conditions: see `docs/decisions/synthetic_only_policy.md`.
