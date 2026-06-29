# LawFirm OS Orchestrator

Canonical machine name: `LawFirm-os-orchestrator`. Human label: Law Firm OS Orchestrator. Plane: execution. Consumes the substrate `LawFirm-os-semantic-substrate` read-only via the canonical orchestrator manifest at `manifests/contract_manifest.v1.json`. For sibling-repo names and authority order across repos, see the substrate's `governance/CROSS_REPO_MAP.md` and this repo's `docs/CANONICAL_ROUTE_MAPPING.md`.

Contract-governed orchestration for law-firm AI systems — not an agent swarm demo.

The MVP is a synthetic-only, local-first, contract-locked evidence-packet factory.

```text
synthetic input
-> pinned Semantic Substrate manifest
-> deterministic route/event-class allowlist validation
-> deterministic mock classifier
-> strict structured-output validation
-> append-only JSONL ledger
-> local evidence packet directory
-> Exception Lake disabled or dry-run by default
```

PR02 adds deterministic local autonomy classification and harness selection:

```text
local action descriptor
-> autonomy gate
-> red/yellow/green decision
-> hardness score
-> leverage scorecard
-> harness selector
-> local harness plan artifact
```

This is execution-plane support only. Risk color controls authority, hardness controls harness depth, and leverage controls priority. Stakes-sensitive escalation is roadmapped for PR07.

PR03 adds deterministic green-lane assumption watching:

```text
green-lane passport
+ local assumption records
+ local signal records
-> assumption mapper
-> red/yellow trigger detector
-> local reclassification recommendation
```

Green lanes are conditional. Signals may downgrade green to yellow or red, but agents may not restore green authority.

PR04 adds inert Codex task packet generation. Packets compress iteration context into local build instructions, but they do not execute Codex, Git, patches, tests, tools, models, network calls, Substrate writes, or Exception Lake writes.

## Quickstart

```bash
python -m pip install -e ".[dev]"
python -m lawfirm_os_orchestrator classify-exception \
  --input examples/synthetic_exception_event.json \
  --substrate tests/fixtures/substrate \
  --lake-mode disabled \
  --stdout json
```

## Safety boundaries

- no real client data;
- no real matter data;
- no production connectors;
- no Semantic Substrate writes;
- no route/event-class invention;
- no Exception Lake writes by default;
- no free-form model text parsing fallback;
- no live model calls in the MVP;
- no scheduled jobs;
- no live Research Radar collection, external APIs, or autonomous research execution;
- contract-lock validation is fail-closed on SHA drift or missing required manifest fields, including `policy_bundle_id`.
- autonomy and harness outputs are local orchestrator records only, not canonical substrate schemas.

## Governance Dependency-Map Mirror

This repo carries `.ai/control/governance-dependency-map-mirror.json` as a local mirror of the upstream governance dependency map in `LawFirm-os-semantic-substrate/registry/governance-dependency-map.json`.

If governance-facing Orchestrator files change, check the upstream governance dependency map and update the local mirror, AI work router, AI table of contents, README, validator, and tests when affected. The mirror is downstream enforcement only; it cannot override Semantic Substrate governance, create canonical route or event authority, authorize external writes, or turn workflow convenience into legal/compliance authority.

## Substrate consumption

The orchestrator loads contracts from a pinned substrate checkout in this order:

1. `manifests/contract_manifest.v1.json` — canonical orchestrator-facing manifest. Required keys: `manifest_id`, `manifest_version`, `policy_bundle_id`, `canonical_schema_keys`, `registry_refs`, `governance_refs`. Loading fail-closes if absent or missing required fields.
2. `registry/exception-route-registry.json` — canonical `route_id`/`event_class` authority.

`policy_bundle_id` is required from the manifest and must not be silently defaulted. See the substrate's `governance/ORCHESTRATOR_BOUNDARY.md` for the full contract.

The substrate is pinned in `contracts.lock.json`. Lock fields:

- `contract_repo: LawFirm-os-semantic-substrate`
- `contract_ref_type: git_sha`
- `contract_sha: <substrate commit>`
- `generated_at: <ISO8601>`
- `generated_by: LawFirm-os-orchestrator`

## Decision-model gates

The orchestrator consumes, but does not own, the Semantic Substrate AI strategy and decision-model doctrine:

- `../LawFirm-os-semantic-substrate/governance/AI_STRATEGY_DOCTRINE.md`
- `../LawFirm-os-semantic-substrate/governance/DECISION_BOTTLENECK_AND_DECISION_MODELS.md`
- `../LawFirm-os-semantic-substrate/registry/decision-model-registry.seed.json`
- `docs/ai-workflow/decision-model-gates.md`
- `docs/decisions/ADR-002-ai-strategy-and-decision-bottleneck.md`

## First throughput metric

Accepted, contract-locked proposed exception packets per reviewer hour.

## PR02 local autonomy and harness commands

```bash
python -m lawfirm_os_orchestrator classify-autonomy \
  --action path/to/action.json \
  --out .lawfirm-os-orchestrator/autonomy/latest.json \
  --stdout json

python -m lawfirm_os_orchestrator select-harness \
  --autonomy .lawfirm-os-orchestrator/autonomy/latest.json \
  --scorecard path/to/scorecard.json \
  --out .lawfirm-os-orchestrator/harness/latest.json \
  --stdout json
```

These commands do not run Git, patch files, call models, call networks, write to the Semantic Substrate, or write to the Exception Lake.

## PR03 local green-lane watcher command

```bash
python -m lawfirm_os_orchestrator watch-green-lanes \
  --signals path/to/signals.json \
  --lanes path/to/green_lanes.json \
  --out .lawfirm-os-orchestrator/autonomy/watch.json \
  --stdout json
```

This command reads local files, writes a local JSON artifact, and can only recommend unchanged, yellow, or red lane status. Human approval is required to restore green.

## PR04 inert Codex task packet command

```bash
python -m lawfirm_os_orchestrator generate-codex-task \
  --opportunity path/to/opportunity.json \
  --scorecard path/to/scorecard.json \
  --autonomy path/to/autonomy.json \
  --harness path/to/harness.json \
  --out .lawfirm-os-orchestrator/harness/codex_task_packet.json \
  --stdout json
```

The packet is a local artifact for human review. Risk color controls authority; hardness and leverage can change review detail, never authority.

## AI Strategy Doctrine Dependency

- Orchestrator consumes AI strategy doctrine from `../LawFirm-os-semantic-substrate/governance/AI_STRATEGY_DOCTRINE.md`.
- Orchestrator may use Legal Context Bundles as pre-model context artifacts.
- Orchestrator emits Evidence Packets as post-model runtime evidence.
- Orchestrator must not define canonical strategy doctrine, context-quality schemas, entropy metric IDs, institutional-knowledge authority, route IDs, or event classes.
- Orchestrator must fail closed or escalate when context quality, provenance, privilege, permission, contract pin, or prompt integrity is insufficient.
