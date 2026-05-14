# AGENTS.md

## Required AI entry behavior

Before making changes in this repository, read:

1. `AI_WORK_START_HERE.md`
2. `../LawFirm-os-semantic-substrate/registry/ai-front-door-registry.json`
3. `../LawFirm-os-semantic-substrate/governance/AI_FRONT_DOOR_BOUNDARY.md`

This repository is one component of the LawFirm OS multi-repo kernel. Do not treat it as standalone.

## Boundary rule

This repository owns execution-plane orchestration, bounded adapters, policy gates, and evidence packet workflows only. It must not define canonical legal meaning, substrate schemas, registries, governance doctrine, route authority, legal document type authority, endpoint authority, or AI front-door routing. Make those changes in `LawFirm-os-semantic-substrate`.

## Required validation

Before reporting success, run `python -m pytest -q` in this repository and the AI front-door integrity gate: `python ../LawFirm-os-semantic-substrate/scripts/validate_ai_front_door.py --substrate-root ../LawFirm-os-semantic-substrate` (from a sibling checkout, adjust paths if your workspace layout differs).

## Canonical names

- Substrate (control plane): `LawFirm-os-semantic-substrate`
- Orchestrator (execution plane): `LawFirm-os-orchestrator` (this repo)
- Evidence Lake (evidence plane): `exceptions-lake-runtime-main`

For full naming and authority order across repos, read the substrate's `governance/CROSS_REPO_MAP.md`.

## Core boundary

Semantic Substrate publishes meaning. Orchestrator executes bounded workflows and builds evidence packets. Exception Lake Runtime validates and records runtime evidence. Humans approve semantic promotion.

The substrate is consumed read-only via the canonical orchestrator manifest at `manifests/contract_manifest.v1.json` in the substrate checkout pinned by `contracts.lock.json`. Required manifest fields must not be silently defaulted; see substrate `governance/ORCHESTRATOR_BOUNDARY.md`.

Before V1 buildout work, read `docs/seed/00_CODEX_READ_FIRST.md` and `docs/CANONICAL_ROUTE_MAPPING.md`.

## PR02 autonomy and harness doctrine

This repo now includes local execution-plane autonomy and harness helpers. They are not canonical substrate authority.

- Risk color controls authority.
- Hardness controls harness depth only.
- Leverage controls priority only.
- Stakes sensitivity remains a PR07 roadmap item.
- Green is limited to synthetic or metadata-only, local, reversible, preapproved-lane work.
- Yellow may draft bounded local evidence or green-candidate recommendations, but cannot restore green.
- Red stops execution authority and may only produce risk memos or human decision packets.

## PR03 green-lane assumption watcher

Green lanes are conditional and assumption-backed. The local watcher may map local signals to lane assumptions and recommend:

- unchanged green when no assumption is affected;
- yellow when assumptions become uncertain, weakened, stale, or review-worthy;
- red when a hard red trigger appears.

Agents may downgrade green or recommend green-candidate. Humans restore or create green authority.

## PR04 inert Codex task packets

Codex task packets are build instructions only. They may summarize objective, allowed paths, forbidden actions, tests, rollback rules, and review requirements.

They must not execute Codex, Git, patches, tests, tools, models, network calls, external APIs, Semantic Substrate writes, Exception Lake writes, production releases, or green restoration.

PR05, PR06, and PR07 remain future phases.

## Stop immediately if a task asks for

- real client or matter data;
- a write to Semantic Substrate;
- route/event-class authoring in this repo;
- production connector writes;
- hidden autonomous writes;
- live Research Radar automation, live model calls, scheduled jobs, or external APIs;
- automatic green restoration;
- treating a Codex task packet as executable authority;
- evidence packet build without manifest hash, source refs, validations, trace IDs, and packet hash.
