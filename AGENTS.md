# AGENTS.md

## Canonical names

- Substrate (control plane): `LawFirm-os-semantic-substrate`
- Orchestrator (execution plane): `LawFirm-os-orchestrator` (this repo)
- Evidence Lake (evidence plane): `exceptions-lake-runtime-main`

For full naming and authority order across repos, read the substrate's `governance/CROSS_REPO_MAP.md`.

## Core boundary

Semantic Substrate publishes meaning. Orchestrator executes bounded workflows and builds evidence packets. Exception Lake Runtime validates and records runtime evidence. Humans approve semantic promotion.

The substrate is consumed read-only via the canonical orchestrator manifest at `manifests/contract_manifest.v1.json` in the substrate checkout pinned by `contracts.lock.json`. Required manifest fields must not be silently defaulted; see substrate `governance/ORCHESTRATOR_BOUNDARY.md`.

Before V1 buildout work, read `docs/seed/00_CODEX_READ_FIRST.md` and `docs/CANONICAL_ROUTE_MAPPING.md`.

## Stop immediately if a task asks for

- real client or matter data;
- a write to Semantic Substrate;
- route/event-class authoring in this repo;
- production connector writes;
- hidden autonomous writes;
- evidence packet build without manifest hash, source refs, validations, trace IDs, and packet hash.
