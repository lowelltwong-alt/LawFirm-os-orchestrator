# AI Table Of Contents

Canonical machine name: `LawFirm-os-orchestrator`. Plane: execution.

This repo executes bounded local workflows and builds evidence packets. It consumes the Semantic Substrate read-only and does not define canonical schemas, route IDs, event classes, governance doctrine, or promotion authority.

## Start Here

- `AI_WORK_START_HERE.md` - current AI work router and stop conditions.
- `AGENTS.md` - agent-facing boundary rules.
- `README.md` - project purpose, quickstart, and safety posture.
- `RECENT_WORK.md` - latest local changes and validation notes.

## Contract Authority

- `contracts.lock.json` - pins the substrate checkout at `LawFirm-os-semantic-substrate` commit `d2ac7f504e67aa00985fbe53aa5350f940e8b529`.
- Substrate `manifests/contract_manifest.v1.json` - canonical orchestrator-facing manifest. Loading is manifest-first.
- Substrate `registry/exception-route-registry.json` - canonical `route_id` and `event_class` authority.
- `docs/CANONICAL_ROUTE_MAPPING.md` - maps local orchestrator labels to substrate authority and marks unmapped labels as non-canonical.

Required manifest fields include `manifest_id`, `manifest_version`, `policy_bundle_id`, `canonical_schema_keys`, and `registry_refs`. The reader fails closed if the manifest is missing or required fields are absent; `policy_bundle_id` must not be silently defaulted.

## Commands And Local Surfaces

- `ENDPOINTS_AND_COMMANDS.md` - current CLI commands and local-only script surfaces.
- `DATA_FLOW_MAP.md` - current execution-plane data flow.
- `scripts/run_evals.py` - offline classify-exception eval runner.
- `scripts/run_shadow_eval.py` - local proposal-only shadow eval runner.
- `scripts/build_upgrade_proposal.py` - local upgrade proposal packet builder.
- `scripts/render_codex_task.py` - inert Codex task draft renderer.
- `scripts/check_safety.py` - safety regression check.

## Learning And Research

- `config/research_sources.yaml` - pre-PR07, metadata-only, non-authoritative source-class mirror. It does not authorize crawling, scheduled jobs, model calls, external APIs, external writes, or production research automation.
- `src/lawfirm_os_orchestrator/discovery/` - local-only Research Radar import helpers.
- `src/lawfirm_os_orchestrator/learning/` - proposal-only learning objects, scoring, shadow evals, proposal packets, recommendations, and task draft rendering.
- `src/lawfirm_os_orchestrator/autonomy/` - PR02 local autonomy gate. Risk color controls authority.
- `src/lawfirm_os_orchestrator/harness/` - PR02 hardness, leverage, and harness selection. Hardness controls harness depth; leverage controls priority.

Phase 2 is partially implemented as local-only scaffolding. Research signals, algorithm insights, shadow evals, upgrade proposals, recommendations, and Codex task drafts are inert artifacts unless a human separately approves future work.

PR02 is implemented as execution-plane local records and CLI artifacts only. It does not define canonical schemas, route IDs, event classes, governance doctrine, or promotion decisions. PR07 will add fuller stakes and reversibility modeling.

## Hard Boundaries

- no Semantic Substrate writes
- no local canonical route or event-class authority
- no real client or matter data
- no live Research Radar automation
- no live web crawling
- no scheduled jobs
- no live model calls
- no external API calls
- no external writes
- no Git operations from inside the application
- Exception Lake mode remains disabled by default and not attempted unless explicitly configured
